
"""
touch_bridge.py

AR1100 resistive touchscreen -> evdev -> Xvfb mouse input.

Features:
- Automatic touchscreen detection
- Configurable active touch area
- Explicit X/Y axis swapping
- Independent axis calibration
- Coordinate inversion
- Mouse clicks, holds and dragging
- Xvfb screen dimension configuration
- Detailed diagnostic logging
"""

import os
import threading
import logging

from evdev import InputDevice, list_devices, ecodes
from Xlib import X, display
from Xlib.ext import xtest


# ============================================================
# CONFIGURATION
# ============================================================

# Xvfb screen dimensions
SCREEN_WIDTH = 1072
SCREEN_HEIGHT = 1448

# Coordinate orientation
SWAP_XY = True
INVERT_X = True
INVERT_Y = False

# Raw touchscreen calibration limits
RAW_MIN_X = 0
RAW_MAX_X = 4095
RAW_MIN_Y = 0
RAW_MAX_Y = 4095

# Active touch area
ACTIVE_MIN_X = 300
ACTIVE_MAX_X = 3700
ACTIVE_MIN_Y = 300
ACTIVE_MAX_Y = 3700

# Screen-coordinate offsets
OFFSET_X = 0
OFFSET_Y = 30

# Logging
DEBUG = True


# ============================================================
# STARTUP CONFIGURATION LOG
# ============================================================

print("=" * 45, flush=True)
print("AR1100 TOUCH DRIVER", flush=True)
print(f"SWAP_XY: {SWAP_XY}", flush=True)
print(f"INVERT_X: {INVERT_X}", flush=True)
print(f"INVERT_Y: {INVERT_Y}", flush=True)
print(f"SCREEN: {SCREEN_WIDTH}x{SCREEN_HEIGHT}", flush=True)
print(f"ACTIVE X: {ACTIVE_MIN_X} - {ACTIVE_MAX_X}", flush=True)
print(f"ACTIVE Y: {ACTIVE_MIN_Y} - {ACTIVE_MAX_Y}", flush=True)
print("=" * 45, flush=True)


logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="[TOUCH] %(message)s"
)

log = logging.getLogger("touch_bridge")


# ============================================================
# DEVICE DETECTION
# ============================================================

def find_touchscreen():

    specified_path = os.environ.get("TOUCH_DEVICE")

    if specified_path:
        device = InputDevice(specified_path)
        log.info(f"Using device: {device.path} ({device.name})")
        return device

    for path in list_devices():

        try:
            device = InputDevice(path)
            capabilities = device.capabilities()

            abs_codes = set(capabilities.get(ecodes.EV_ABS, []))
            key_codes = set(capabilities.get(ecodes.EV_KEY, []))

            has_touch_button = (
                ecodes.BTN_TOUCH in key_codes
                or ecodes.BTN_LEFT in key_codes
            )

            if (
                ecodes.ABS_X in abs_codes
                and ecodes.ABS_Y in abs_codes
                and has_touch_button
            ):
                log.info(
                    f"Found touchscreen: {device.path} ({device.name})"
                )
                return device

            device.close()

        except Exception:
            continue

    raise RuntimeError(
        "No compatible touchscreen found. "
        "Set TOUCH_DEVICE to /dev/input/eventX"
    )


# ============================================================
# CALIBRATION
# ============================================================

class TouchCalibration:

    def __init__(self, device):

        self.raw_min_x = RAW_MIN_X
        self.raw_max_x = RAW_MAX_X
        self.raw_min_y = RAW_MIN_Y
        self.raw_max_y = RAW_MAX_Y

        self.active_min_x = (
            ACTIVE_MIN_X if ACTIVE_MIN_X is not None
            else self.raw_min_x
        )

        self.active_max_x = (
            ACTIVE_MAX_X if ACTIVE_MAX_X is not None
            else self.raw_max_x
        )

        self.active_min_y = (
            ACTIVE_MIN_Y if ACTIVE_MIN_Y is not None
            else self.raw_min_y
        )

        self.active_max_y = (
            ACTIVE_MAX_Y if ACTIVE_MAX_Y is not None
            else self.raw_max_y
        )

        if self.raw_min_x >= self.raw_max_x:
            raise ValueError("Invalid raw X range")

        if self.raw_min_y >= self.raw_max_y:
            raise ValueError("Invalid raw Y range")

        if self.active_min_x >= self.active_max_x:
            raise ValueError("Invalid active X range")

        if self.active_min_y >= self.active_max_y:
            raise ValueError("Invalid active Y range")

        log.info(
            f"Raw X: {self.raw_min_x} - {self.raw_max_x}"
        )

        log.info(
            f"Raw Y: {self.raw_min_y} - {self.raw_max_y}"
        )

        log.info(
            f"Active X: {self.active_min_x} - {self.active_max_x}"
        )

        log.info(
            f"Active Y: {self.active_min_y} - {self.active_max_y}"
        )

    def inside_active_area(self, raw_x, raw_y):

        return (
            self.active_min_x <= raw_x <= self.active_max_x
            and
            self.active_min_y <= raw_y <= self.active_max_y
        )

    @staticmethod
    def normalize(value, minimum, maximum):

        return (value - minimum) / (maximum - minimum)

    def transform(self, raw_x, raw_y, screen_width, screen_height):

        # ----------------------------------------------------
        # EXPLICIT AXIS SELECTION
        # ----------------------------------------------------

        if SWAP_XY is True:

            mapped_x = raw_y
            mapped_y = raw_x

            min_x = self.active_min_y
            max_x = self.active_max_y

            min_y = self.active_min_x
            max_y = self.active_max_x

        else:

            mapped_x = raw_x
            mapped_y = raw_y

            min_x = self.active_min_x
            max_x = self.active_max_x

            min_y = self.active_min_y
            max_y = self.active_max_y

        # ----------------------------------------------------
        # NORMALIZATION
        # ----------------------------------------------------

        x = self.normalize(mapped_x, min_x, max_x)
        y = self.normalize(mapped_y, min_y, max_y)

        # ----------------------------------------------------
        # INVERSION
        # ----------------------------------------------------

        if INVERT_X:
            x = 1.0 - x

        if INVERT_Y:
            y = 1.0 - y

        # ----------------------------------------------------
        # SCREEN COORDINATES
        # ----------------------------------------------------

        screen_x = round(x * (screen_width - 1))
        screen_y = round(y * (screen_height - 1))

        screen_x += OFFSET_X
        screen_y += OFFSET_Y

        screen_x = max(0, min(screen_x, screen_width - 1))
        screen_y = max(0, min(screen_y, screen_height - 1))

        # ----------------------------------------------------
        # DIAGNOSTICS
        # ----------------------------------------------------

        print(
            f"[MAP] SWAP_XY={SWAP_XY} "
            f"raw=({raw_x},{raw_y}) "
            f"mapped=({mapped_x},{mapped_y}) "
            f"normalized=({x:.3f},{y:.3f}) "
            f"screen=({screen_x},{screen_y})",
            flush=True
        )

        return screen_x, screen_y


# ============================================================
# XVFB MOUSE
# ============================================================

class VirtualMouse:

    def __init__(self):

        display_name = os.environ.get("DISPLAY")

        if not display_name:
            raise RuntimeError("DISPLAY is not set")

        self.display = display.Display(display_name)

        if not self.display.has_extension("XTEST"):
            raise RuntimeError("X server does not support XTEST")

        screen = self.display.screen()

        self.width = (
            SCREEN_WIDTH
            if SCREEN_WIDTH is not None
            else screen.width_in_pixels
        )

        self.height = (
            SCREEN_HEIGHT
            if SCREEN_HEIGHT is not None
            else screen.height_in_pixels
        )

        self.button_pressed = False
        self.lock = threading.Lock()

        log.info(f"X display: {display_name}")
        log.info(f"Xvfb resolution: {self.width}x{self.height}")

    def move(self, x, y):

        with self.lock:

            xtest.fake_input(
                self.display,
                X.MotionNotify,
                x=x,
                y=y
            )

            self.display.sync()

    def press(self):

        with self.lock:

            if self.button_pressed:
                return

            xtest.fake_input(
                self.display,
                X.ButtonPress,
                1
            )

            self.display.sync()
            self.button_pressed = True

    def release(self):

        with self.lock:

            if not self.button_pressed:
                return

            xtest.fake_input(
                self.display,
                X.ButtonRelease,
                1
            )

            self.display.sync()
            self.button_pressed = False

    def close(self):

        self.release()
        self.display.close()


# ============================================================
# TOUCH READER
# ============================================================

class TouchReader:

    def __init__(self):

        self.device = find_touchscreen()
        self.calibration = TouchCalibration(self.device)
        self.mouse = VirtualMouse()

        self.raw_x = self.calibration.raw_min_x
        self.raw_y = self.calibration.raw_min_y

        self.touching = False
        self.mouse_down = False
        self.running = False

        key_codes = set(
            self.device.capabilities().get(ecodes.EV_KEY, [])
        )

        self.touch_code = (
            ecodes.BTN_TOUCH
            if ecodes.BTN_TOUCH in key_codes
            else ecodes.BTN_LEFT
        )

        log.info(f"Touch button code: {self.touch_code}")
        log.info("Touch reader initialized")

    # ========================================================
    # PROCESS FRAME
    # ========================================================

    def process_frame(self):

        # RELEASE
        if not self.touching:

            if self.mouse_down:

                print("[TOUCH] RELEASE", flush=True)

                self.mouse.release()
                self.mouse_down = False

            return

        # CHECK ACTIVE AREA
        inside = self.calibration.inside_active_area(
            self.raw_x,
            self.raw_y
        )

        # NEW TOUCH
        if not self.mouse_down:

            print(
                f"[TOUCH] DOWN "
                f"raw=({self.raw_x},{self.raw_y}) "
                f"inside_active_area={inside}",
                flush=True
            )

            if not inside:
                return

            self.mouse_down = True

        # CLAMP TO ACTIVE AREA
        x = max(
            self.calibration.active_min_x,
            min(self.raw_x, self.calibration.active_max_x)
        )

        y = max(
            self.calibration.active_min_y,
            min(self.raw_y, self.calibration.active_max_y)
        )

        # TRANSFORM
        screen_x, screen_y = self.calibration.transform(
            x,
            y,
            self.mouse.width,
            self.mouse.height
        )

        print(
            f"[TOUCH] MOVE raw=({self.raw_x},{self.raw_y}) "
            f"screen=({screen_x},{screen_y})",
            flush=True
        )

        self.mouse.move(screen_x, screen_y)

        # PRESS
        if not self.mouse.button_pressed:
            self.mouse.press()

    # ========================================================
    # EVENT LOOP
    # ========================================================

    def run(self):

        self.running = True

        log.info("Touch driver running")

        try:

            for event in self.device.read_loop():

                if not self.running:
                    break

                if event.type == ecodes.EV_ABS:

                    if event.code == ecodes.ABS_X:
                        self.raw_x = event.value

                    elif event.code == ecodes.ABS_Y:
                        self.raw_y = event.value

                elif event.type == ecodes.EV_KEY:

                    if event.code == self.touch_code:
                        self.touching = bool(event.value)

                elif (
                    event.type == ecodes.EV_SYN
                    and event.code == ecodes.SYN_REPORT
                ):

                    self.process_frame()

        except OSError as exc:

            log.error(f"Touch device error: {exc}")

        except Exception as exc:

            log.exception(f"Touch driver failed: {exc}")

        finally:

            self.stop()

    # ========================================================
    # CLEANUP
    # ========================================================

    def stop(self):

        self.running = False

        try:
            self.mouse.release()
            self.mouse.close()
            self.device.close()

        except Exception:
            pass

        log.info("Touch driver stopped")


# ============================================================
# PUBLIC API
# ============================================================

_reader = None
_thread = None


def start_touch_reader():

    global _reader, _thread

    if _thread is not None and _thread.is_alive():
        log.warning("Touch driver already running")
        return _thread

    _reader = TouchReader()

    _thread = threading.Thread(
        target=_reader.run,
        name="TouchReader",
        daemon=True
    )

    _thread.start()

    return _thread


def stop_touch_reader():

    global _reader, _thread

    if _reader is not None:
        _reader.stop()
        _reader = None

    _thread = None
