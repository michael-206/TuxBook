from guizero import Box, Text, PushButton
import json
import os
import math

def build(parent, **kwargs):

    load_app = kwargs["load_app"]

    title = Text(
        parent,
        text="All Apps",
        size=48
    )


    apps_directory = "apps"

    apps_grid = Box(parent, layout="grid", width="fill", height="fill")

    index = 0
    buttons = []

    for app_folder in os.listdir(apps_directory):

        app_path = os.path.join(
            apps_directory,
            app_folder
        )

        # Make sure it's a directory
        if not os.path.isdir(app_path):
            continue

        info_path = os.path.join(
            app_path,
            "info.json"
        )

        # Make sure metadata exists
        if not os.path.exists(info_path):
            continue

        # Read metadata
        with open(info_path, "r") as file:
            info = json.load(file)

        app_name = info["name"]

        grid_pos = [index % 3, index // 3]

        print(f"App: {app_name} is being positioned at {grid_pos} and its index is {index}")

        button = PushButton(
            apps_grid,
            grid = grid_pos,
            text=app_name,
            command=lambda name=app_folder: load_app(name)
        )
        button.text_size = 32
        buttons.append(button)

        index += 1

    for btn in buttons:
        btn.tk.grid_configure(sticky="nsew", padx=10, pady=10)

    for col in range(3):
        apps_grid.tk.grid_columnconfigure(col, weight=1, uniform="col_group")

    total_rows = math.ceil(index / 3)
    for row in range(total_rows):
        apps_grid.tk.grid_rowconfigure(row, weight=1, uniform="row_group")
