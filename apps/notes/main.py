from guizero import PushButton, Text


def build(parent, **kwargs):
    navigate = kwargs.get("navigate")

    Text(parent, text="Notes", size=36)

    PushButton(
        parent,
        text="Editor",
        command=lambda: navigate("editor") if navigate else None,
    )