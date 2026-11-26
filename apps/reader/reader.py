
from guizero import Text, TextBox
from tinydb import TinyDB, Query
import datetime
from epub_utils import EpubBook

Book = Query()

db = TinyDB("db.json")

books = db.table("Books")
history = db.table("Reading History")

def build(parent, **kwargs):
    navigate = kwargs['navigate']
    book_id = kwargs['data']

    books.update(
        {'last_opened': str(datetime.datetime.now())},
        doc_ids=[book_id]
    )

    book = EpubBook('books/'+books.get(doc_id=book_id)['filename'])

    print("TITLE:", book.title)
    print("CHAPTERS:", book.chapter_count)

    if book.chapter_count:
        print("CHAPTER TITLE:", book.chapters[0]["title"])
        print("TEXT:", repr(book.chapters[0]["text"][:500]))

    Text(parent, text=book.title, size=18)
    TextBox(
        parent,
        text=book.chapters[50]["text"],
        width=55,
        height=28,
        multiline=True,
        scrollbar=True,
        enabled=False,
    )

    history.insert({"book_doc_id":book_id, "start":str(datetime.datetime.now()), "end":None})
