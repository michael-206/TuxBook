import configparser
import importlib
import json
import os
from pathlib import Path
from guizero import App, Box, Text, PushButton
import datetime
import platform
import tkinter as tk

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
keyboard_icon = Text(header, align="right", text="⌨", size=48)
keyboard_icon.tk.bind("<Button-1>", lambda event: toggle_keyboard())

header_stuff = [header_text, search_icon, sync_icon, wifi_icon, bell_icon, brightness_icon, keyboard_icon]

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
# On-screen keyboard
# --------------------------------------------------

# The keyboard is a native Tkinter frame placed over the lower part of
# the content area. It does not replace or modify the app currently open.
keyboard_height = 350
keyboard_visible = False
keyboard_target = None
keyboard_shift = False

keyboard_frame = tk.Frame(
    root.tk,
    bg="#eeeeee",
    bd=2,
    relief="solid"
)

# Use a 12-column grid so the modifier and spacebar keys can be wider.
for column in range(12):
    keyboard_frame.grid_columnconfigure(column, weight=1, uniform="keyboard")
for row in range(4):
    keyboard_frame.grid_rowconfigure(row, weight=1, uniform="keyboard")

keyboard_buttons = {}

def _remember_keyboard_target(event):
    """Remember the last text-entry widget touched by the user."""
    global keyboard_target

    widget = event.widget
    try:
        widget_class = widget.winfo_class()
        if widget_class in ("Entry", "Text", "TEntry", "TCombobox", "Spinbox"):
            keyboard_target = widget
            show_keyboard()
    except tk.TclError:
        pass


def show_keyboard():
    global keyboard_visible
    if not keyboard_visible:
        keyboard_frame.place(
            relx=0.5,
            rely=1.0,
            y=-120,                 # Keep the 120px bottom navigation visible.
            anchor="s",
            relwidth=1.0,
            height=keyboard_height
        )
        keyboard_frame.lift()
        keyboard_visible = True


def hide_keyboard():
    global keyboard_visible
    keyboard_frame.place_forget()
    keyboard_visible = False


def toggle_keyboard():
    if keyboard_visible:
        hide_keyboard()
    else:
        show_keyboard()


def _insert_text(value):
    """Insert a character into the last focused input, not the key button."""
    global keyboard_target, keyboard_shift

    widget = keyboard_target
    if widget is None:
        return

    try:
        if not widget.winfo_exists():
            keyboard_target = None
            return

        widget_class = widget.winfo_class()

        # Replace selected text if there is a selection.
        try:
            widget.delete("sel.first", "sel.last")
        except tk.TclError:
            pass

        if widget_class == "Text":
            widget.insert("insert", value)
        else:
            widget.insert("insert", value)

        if keyboard_shift and value.isalpha():
            keyboard_shift = False
            _refresh_keyboard_labels()

    except tk.TclError:
        keyboard_target = None


def _backspace():
    widget = keyboard_target
    if widget is None:
        return

    try:
        if not widget.winfo_exists():
            return

        try:
            widget.delete("sel.first", "sel.last")
            return
        except tk.TclError:
            pass

        if widget.winfo_class() == "Text":
            if widget.compare("insert", ">", "1.0"):
                widget.delete("insert-1c", "insert")
        else:
            cursor = widget.index("insert")
            if cursor > 0:
                widget.delete(cursor - 1, cursor)
    except tk.TclError:
        pass


def _enter():
    widget = keyboard_target
    if widget is None:
        return

    try:
        if widget.winfo_exists():
            if widget.winfo_class() == "Text":
                widget.insert("insert", "\n")
            else:
                widget.event_generate("<Return>")
    except tk.TclError:
        pass


def _toggle_shift():
    global keyboard_shift
    keyboard_shift = not keyboard_shift
    _refresh_keyboard_labels()


def _add_key(row, column, span, label, command, key_name=None):
    button = tk.Button(
        keyboard_frame,
        text=label,
        command=command,
        font=("Arial", 22),
        bg="#ffffff",
        fg="#111111",
        activebackground="#dddddd",
        activeforeground="#111111",
        relief="raised",
        bd=1,
        takefocus=False
    )
    button.grid(
        row=row,
        column=column,
        columnspan=span,
        sticky="nsew",
        padx=3,
        pady=3
    )
    if key_name:
        keyboard_buttons[key_name] = button
    return button


def _refresh_keyboard_labels():
    for letter, button in keyboard_buttons.items():
        button.configure(text=letter.upper() if keyboard_shift else letter.lower())


# Row 1: QWERTY
for index, letter in enumerate("qwertyuiop"):
    _add_key(0, index, 1, letter, lambda char=letter: _insert_text(
        char.upper() if keyboard_shift else char
    ), key_name=letter)

# Row 2: ASDF row, centered
for index, letter in enumerate("asdfghjkl", start=1):
    _add_key(1, index, 1, letter, lambda char=letter: _insert_text(
        char.upper() if keyboard_shift else char
    ), key_name=letter)

# Row 3: Shift, letters, and backspace
_add_key(2, 0, 2, "⇧", _toggle_shift)
for index, letter in enumerate("zxcvbnm", start=2):
    _add_key(2, index, 1, letter, lambda char=letter: _insert_text(
        char.upper() if keyboard_shift else char
    ), key_name=letter)
_add_key(2, 9, 3, "⌫", _backspace)

# Row 4: punctuation, space, enter, and dismiss
_add_key(3, 0, 2, "?123", lambda: _insert_text("?"))
_add_key(3, 2, 1, ",", lambda: _insert_text(","))
_add_key(3, 3, 5, "Space", lambda: _insert_text(" "))
_add_key(3, 8, 1, ".", lambda: _insert_text("."))
_add_key(3, 9, 2, "↵", _enter)
_add_key(3, 11, 1, "↓", hide_keyboard)

# Show the keyboard whenever the user taps a supported text-entry widget.
# The target widget is remembered before the keyboard's own buttons are used.
root.tk.bind_all("<FocusIn>", _remember_keyboard_target, add="+")


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

