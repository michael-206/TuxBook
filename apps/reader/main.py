from guizero import Box, Text
from tinydb import TinyDB


def build(parent, **kwargs):
    navigate = kwargs["navigate"]

    Text(parent, text="EPUB Reader", size=18)

    db = TinyDB("db.json")
    books = db.table("Books")

    for book in books.all():
        book_frame = Box(parent, width="fill", border=True, align="top", height=200)

        title = Text(
            book_frame,
            text=book["title"],
            size=48,
            align="left",
            width="fill",
        )

        finished = Text(
            book_frame,
            text="Finished" if book["finished"] else "Unfinished",
            size=24,
            align="right",
        )

        author = Text(
            book_frame,
            text=book["author"],
            size=32,
            align="left",
            width="fill",
        )

        size_text = Text(
            book_frame,
            text=book["size"],
            size=24,
            align="right",
        )

        print(book["title"], book["author"], book["size"])

        def open_book(book_id, widget=None):
            navigate("reader", data=book_id)

        for widget in (book_frame, title, finished, author, size_text):
            widget.when_clicked = lambda book_id=book.doc_id: open_book(book_id)
