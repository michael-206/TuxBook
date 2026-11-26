from guizero import Text


def build(parent, **kwargs):
    Text(parent, text="Basic Math", size=24)
    Text(parent, text="2 + 2 is 4", size=14)
    Text(parent, text="3 - 1 is 2", size=14)