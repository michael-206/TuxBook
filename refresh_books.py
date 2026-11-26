from tinydb import TinyDB, Query
from ebooklib import epub
import os
import datetime

db = TinyDB("db.json")

books = db.table('Books')

books.remove(all)

books_list = os.listdir('books/')\

for count, i in enumerate(books_list):

    book = epub.read_epub("books/"+i)

    title = book.get_metadata('DC', 'title')[0][0]

    creator = book.get_metadata('DC', 'creator')[0][0]

    size = os.path.getsize("books/"+i) / (1024*1024)

    size = round(size, 1)

    size = str(size) + " MB"

    books.insert({"title":title, "author":creator, "size": size, "filename":i, "current_chap":0, "chap_position":0, "last_updated":str(datetime.datetime.now()), "last_opened": 0, "finished":False, "reading_time":0})

    print(f"Done {count+1}/{len(books_list)} Books\r")

