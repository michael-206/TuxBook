import configparser
import importlib
import json
import os
from pathlib import Path
from guizero import App, Box, Text, PushButton
import datetime
import platform

# Get the directory of the current file
BASE_DIR = Path(__file__).parent.resolve()

config = configparser.ConfigParser()
config_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "config.ini"
)
config.read(config_path)

pinned_app_1 = config["PINNED_APPS"]["app1"]
pinned_app_2 = config["PINNED_APPS"]["app2"]
pinned_app_3 = config["PINNED_APPS"]["app3"]

root = App(title="Linux Ereader OS", width=1072, height=1448, bg="#ffffff")
# Force app window to take focus on startup and keep it
root.tk.focus_force()

root.tk.option_add("*Button.borderWidth", 0)
root.tk.option_add("*Button.highlightThickness", 0)
root.tk.option_add("*Button.relief", "flat")
#root.tk.option_add("*Button.compound", "top")

def get_app_info(name):
    app_path = os.path.join("apps", name)
    info_path = os.path.join(app_path, "info.json")

    with open(info_path, "r") as file:
        info = json.load(file)

    return info

def get_app_icon(name):
    app_path = os.path.join("apps", name)
    info_path = os.path.join(app_path, "info.json")

    with open(info_path, "r") as file:
        info = json.load(file)

    return os.path.join(app_path, info["icon"])



# --------------------------------------------------
# Header
# --------------------------------------------------

header = Box(root, align="top", width="fill", height=80)



header_text = Text(header, align="left", text="00:00", size=48)

search_icon = Text(header, align="right", text="🔎", size=48)
sync_icon = Text(header, align="right", text="🔄️", size=48)
wifi_icon = Text(header, align="right", text="🛜", size=48)
bell_icon = Text(header, align="right", text="🔔", size=48)
brightness_icon = Text(header, align="right", text="🔆", size=48)

header_stuff = [header_text, search_icon, sync_icon, wifi_icon, bell_icon, brightness_icon]

for item in header_stuff:
    item.tk.pack_configure(padx=10, ipady=10)

# --------------------------------------------------
# Bottom navigation
# --------------------------------------------------


bottom_bar = Box(root, align="bottom", layout="grid", width="fill", height=120)

line = Box(root, height=2, width="fill", align="bottom")
line.bg = "black"


home_button = PushButton(
    bottom_bar,
    text="Home",
    grid=[0, 0],
    image=get_app_icon("home"),
    command=lambda: load_app("home"),
)

pinned_button_1 = PushButton(
    bottom_bar,
    text=get_app_info(pinned_app_1)["name"],
    grid=[1, 0],
    image=get_app_icon(pinned_app_1),
    command=lambda: load_app(pinned_app_1),
)

pinned_button_2 = PushButton(
    bottom_bar,
    text=get_app_info(pinned_app_2)["name"],
    grid=[2, 0],
    image=get_app_icon(pinned_app_2),
    command=lambda: load_app(pinned_app_2),
)

pinned_button_3 = PushButton(
    bottom_bar,
    text=get_app_info(pinned_app_3)["name"],
    grid=[3, 0],
    image=get_app_icon(pinned_app_3),
    command=lambda: load_app(pinned_app_3),
)

apps_button = PushButton(
    bottom_bar,
    text="Apps",
    grid=[4, 0],
    image=get_app_icon("all_apps"),
    command=lambda: load_app("all_apps"),
)

# Configure the 5 grid columns to expand equally across the full width
for i in range(5):
    bottom_bar.tk.grid_columnconfigure(i, weight=1, uniform="buttons")
bottom_bar.tk.grid_rowconfigure(0, weight=1)

# Make each button fill its grid cell completely
buttons = [
    home_button,
    pinned_button_1,
    pinned_button_2,
    pinned_button_3,
    apps_button,
]
for btn in buttons:
    btn.tk.grid(sticky="nsew")
    #btn.bg = bottom_bar.bg
    #btn.tk.config(
    #    bd=0,
    #    highlightthickness=0,
    #    relief="flat",
    #)


def wrap_button_text(event):
    wraplength = max(1, event.width // len(buttons) - 16)
    for btn in buttons:
        if btn.tk.cget("wraplength") != wraplength:
            btn.tk.configure(wraplength=wraplength)


bottom_bar.tk.bind("<Configure>", wrap_button_text)

for btn in buttons:
    btn.tk.configure(
        font=("Arial", 32),
        foreground="#000000",
        background="#ffffff",
        activeforeground="#000000",
        activebackground="#ffffff",
        justify="center",
        anchor="center",
    )


def update_pinned_apps():
    config.read(BASE_DIR / "config.ini")

    p1 = config["PINNED_APPS"]["app1"]
    p2 = config["PINNED_APPS"]["app2"]
    p3 = config["PINNED_APPS"]["app3"]


    pinned_button_1.text = get_app_info(p1)["name"]
    pinned_button_1.when_clicked =lambda: load_app(p1)
    pinned_button_1.image = get_app_icon(p1)
    pinned_button_2.text = get_app_info(p2)["name"]
    pinned_button_2.when_clicked =lambda: load_app(p2)
    pinned_button_2.image = get_app_icon(p2)
    pinned_button_3.text = get_app_info(p3)["name"]
    pinned_button_3.when_clicked =lambda: load_app(p3)
    pinned_button_3.image = get_app_icon(p3)



# --------------------------------------------------
# Content area
# --------------------------------------------------

content_frame = Box(root, align="top", width="fill", height="fill")

# --------------------------------------------------
# App loading
# --------------------------------------------------


def load_app(app_name, data=None):

    print("app loading in progress")

    app_path = os.path.join("apps", app_name)
    info_path = os.path.join(app_path, "info.json")

    with open(info_path, "r") as file:
        info = json.load(file)

    entrypoint = info["entrypoint"]
    load_screen(app_name, entrypoint, data=data)


def load_screen(app_name, screen_name, data=None):
    # Wipe all child widgets from the frame.
    for widget in content_frame.tk.winfo_children():
        widget.destroy()
    content_frame.children.clear()

    # Import screen dynamically
    screen = importlib.import_module(f"apps.{app_name}.{screen_name}")

    def navigate(destination, data=None):
        load_screen(app_name, destination, data=data)

    screen.build(
        content_frame,
        navigate=navigate,
        load_app=load_app,
        update_pinned_apps=update_pinned_apps,
        data=data,
    )


# --------------------------------------------------
# Start OS
# --------------------------------------------------

load_app("home")


def get_time():
    header_text.value = datetime.datetime.now().strftime("%H:%M")


# Import the display bridge after the GUI is created.
if platform.system() == "Linux":
    from display_bridge import update_display

    refresh = 60

    def refresh_eink():
        global refresh
        try:
            if refresh > 0:
                update_display()
                refresh =- 1
            else:
                update_display(partial=True)
                refresh = 60
        except Exception as exc:
            print(f"Display update failed: {exc}")

    from touch_bridge import start_touch_reader

    start_touch_reader()

    print("GUI DISPLAY:", os.environ.get("DISPLAY"), flush=True)
    root.repeat(1000, refresh_eink)
else:
    from ui_scale import SCALE, s, apply_scale
    apply_scale(root)

header_text.repeat(1000, get_time)

root.display()

