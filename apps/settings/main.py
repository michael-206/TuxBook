import configparser
import json
import os
from pathlib import Path

from guizero import Combo, Text

BASE_DIR = Path(__file__).resolve().parents[2]

config = configparser.ConfigParser()
config.read(BASE_DIR / "config.ini")

WIDTH="fill"
HEIGHT="fill"
TEXT_SIZE=32
def select_pinned_app(number, app_name, update_pinned_apps):
    config["PINNED_APPS"][f"app{number}"] = app_name

    with open(BASE_DIR / "config.ini", "w") as file:
        config.write(file)

    update_pinned_apps()


def build(parent, **kwargs):
    update_pinned_apps = kwargs["update_pinned_apps"]
    options = []
    app_pairs = {}

    Text(parent, text="Settings", size=24)

    apps_directory = "apps"

    for app_folder in os.listdir(apps_directory):
        app_path = os.path.join(apps_directory, app_folder)

        if not os.path.isdir(app_path):
            continue

        info_path = os.path.join(app_path, "info.json")
        if not os.path.exists(info_path):
            continue

        with open(info_path, "r") as file:
            info = json.load(file)

        app_name = info["name"]
        options.append(app_name)
        app_pairs[app_name] = app_folder

    combo1 = Combo(
        parent,
        options=options,
        width=WIDTH,
        height=HEIGHT,
        selected=next(
            (
                app_name
                for app_name, app_folder in app_pairs.items()
                if app_folder == config["PINNED_APPS"]["app1"]
            ),
            None,
        ),
        command=lambda app_name: select_pinned_app(
            1, app_pairs[app_name], update_pinned_apps
        ),
    )
    combo2 = Combo(
        parent,
        options=options,
        width=WIDTH,
        height=HEIGHT,
        selected=next(
            (
                app_name
                for app_name, app_folder in app_pairs.items()
                if app_folder == config["PINNED_APPS"]["app2"]
            ),
            None,
        ),
        command=lambda app_name: select_pinned_app(
            2, app_pairs[app_name], update_pinned_apps
        ),
    )

    combo3 = Combo(
        parent,
        options=options,
        width=WIDTH,
        height=HEIGHT,
        selected=next(
            (
                app_name
                for app_name, app_folder in app_pairs.items()
                if app_folder == config["PINNED_APPS"]["app3"]
            ),
            None,
        ),
        command=lambda app_name: select_pinned_app(
            3, app_pairs[app_name], update_pinned_apps
        ),
    )
    combo1.text_size = TEXT_SIZE
    combo2.text_size = TEXT_SIZE
    combo3.text_size = TEXT_SIZE
