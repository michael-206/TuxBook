import os
from pathlib import Path

from PIL import Image, ImageGrab

WIDTH = 1072
HEIGHT = 1448

# Set DISPLAY_BACKEND=hardware to use a connected IT8951.
BACKEND = os.environ.get("DISPLAY_BACKEND", "virtual").lower()

display = None

if BACKEND == "hardware":
    from IT8951.display import AutoEPDDisplay
    from IT8951.constants import DisplayModes

    # The HD panel is physically 1448 x 1072 in landscape.
    # Rotate the framebuffer into portrait orientation.
    display = AutoEPDDisplay(
        vcom=-2.82,
        rotate="CW",
        spi_hz=24000000,
    )

    print(
        "IT8951 initialized:",
        display.width,
        "x",
        display.height,
    )

    if (display.width, display.height) != (WIDTH, HEIGHT):
        raise RuntimeError(
            f"Unexpected display size: "
            f"{display.width} x {display.height}"
        )

    display.clear()


def update_display(partial=True):
    """Capture Xvfb and update the e-reader display."""
    screenshot = ImageGrab.grab()
    screenshot = screenshot.convert("L")

    if screenshot.size != (WIDTH, HEIGHT):
        screenshot = screenshot.resize(
            (WIDTH, HEIGHT),
            Image.Resampling.LANCZOS,
        )

    if display is None:
        # Virtual-only mode: save a preview without hardware.
        screenshot.save("/tmp/linux-ereader-preview.png")
        return

    # Copy the screenshot into Greg's display framebuffer.
    display.frame_buf.paste(screenshot)

    if partial:
    # Update only the changed pixels.
        display.draw_partial(DisplayModes.GC16)

    else:
        display.draw_full(2)
