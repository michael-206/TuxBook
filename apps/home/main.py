from guizero import Text, TextBox


def build(parent, **kwargs):
    navigate = kwargs.get("navigate")
    load_app = kwargs.get("load_app")

    # Everything in this app goes inside the provided frame
    title = Text(parent, text="Home Screen", size=32)

    message = Text(
        parent, text="This is the Home screen app.", size=32
    )

    box = TextBox(parent, width=200, height=100)
