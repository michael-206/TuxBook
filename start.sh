
#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

source ./venv/bin/activate

export DISPLAY_BACKEND="${DISPLAY_BACKEND:-hardware}"

# Replace this with your actual AR1100 event device.
export TOUCH_DEVICE="${TOUCH_DEVICE:-/dev/input/event2}"

exec xvfb-run -a \
    -s "-screen 0 1072x1448x24" \
    python3 main_os.py

