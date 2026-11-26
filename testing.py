
from pywinusb import hid

VID = 0x04D8
PID = 0x0C02  # AR1100 HID-MOUSE mode


def handle_report(data):
    # Print the raw bytes first, so we can verify the report layout.
    raw = list(data)
    print("RAW:", " ".join(f"{b:02X}" for b in raw))

    # HID-MOUSE reports contain 5 bytes:
    # buttons, X low, X high, Y low, Y high.
    # pywinusb may include a report-ID byte at the start.
    candidates = [raw]

    if len(raw) >= 6:
        candidates.append(raw[1:])

    report = next((r for r in candidates if len(r) == 5), None)
    if report is None:
        return

    buttons, x_low, x_high, y_low, y_high = report

    x = ((x_high & 0x0F) << 8) | x_low
    y = ((y_high & 0x0F) << 8) | y_low

    print(f"RAW COORDINATES: X={x}, Y={y}")


devices = hid.HidDeviceFilter(
    vendor_id=VID,
    product_id=PID
).get_devices()

if not devices:
    print("AR1100 not found in HID-MOUSE mode.")
    print("Check Device Manager and the USB VID/PID.")
    raise SystemExit(1)

device = devices[0]
print("Device:", device.product_name)
print("Opening device...")

try:
    device.open()
    device.set_raw_data_handler(handle_report)

    print("Touch the screen. Press Ctrl+C to exit.")

    while True:
        input()

except KeyboardInterrupt:
    print("\nExiting.")

finally:
    device.close()
 