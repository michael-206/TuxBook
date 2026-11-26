from guizero import PushButton, Text


def build(parent, **kwargs):
    navigate = kwargs["navigate"]

    Text(parent, text="Note Editor", size=24)
    PushButton(
        parent,
        text="Back",
        command=lambda: navigate("main")
    )