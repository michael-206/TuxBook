from guizero import Text

def build(parent, **kwargs):
    # Guizero text elements automatically parent to parent
    title = Text(parent, text="Hello World!", size=48)
    message = Text(parent, text="This is the Hello World app.", size=24)