from fastapi import FastAPI, Body

INITIAL_BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'},
]

def reset_books():
    global BOOKS
    BOOKS = INITIAL_BOOKS.copy()


app = FastAPI()


@app.get("/books")
async def read_all_books():
    return BOOKS


@app.get("/books/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get("title").casefold() == book_title.casefold():
            return book


@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get("category").casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return



@app.get("/books/author/{book_author}")
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if (
            book.get("author").casefold() == book_author.casefold()
            and book.get("category").casefold() == category.casefold()
        ):
            books_to_return.append(book)
    return books_to_return



@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)
    return BOOKS


@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i, b in enumerate(BOOKS):
        if b.get("title").casefold() == updated_book.get("title").casefold():
            BOOKS[i] = updated_book


@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i, b in enumerate(BOOKS):
        if b.get("title").casefold() == book_title.casefold():
            BOOKS.pop(i)
            break

@app.get("/books/author_books/{book_author}")
async def fetch_author_books(book_author: str):
    author_books = []
    for b in BOOKS:
        if b.get("author").casefold() == book_author.casefold():
            author_books.append(b)
    return author_books









