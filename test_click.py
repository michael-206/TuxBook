
import time
from Xlib import X, display
from Xlib.ext import xtest

d = display.Display()
root = d.screen().root

print("Connected to:", d.get_display_name())
print("Clicking at 500, 500 in 3 seconds...")
time.sleep(3)

xtest.fake_input(
    d, X.MotionNotify,
    x=500, y=500, root=root
)
d.sync()

xtest.fake_input(d, X.ButtonPress, detail=1)
d.sync()

time.sleep(0.1)

xtest.fake_input(d, X.ButtonRelease, detail=1)
d.sync()

print("Click injected.")
