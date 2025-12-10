from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not needed on create", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=6)
    published_date: int = Field(gt=1000, lt=2100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "coder",
                "description": "new description",
                "rating": 5,
                "published_date": 2026,
            }
        }
    }


BOOKS = [
    Book(1, "Computer Science Pro", "coding", "A very nice book!", 5, 2030),
    Book(2, "Be Fast with FastAPI", "coding", "A great book!", 5, 2030),
    Book(3, "Master Endpoints", "coding", "A awesome book!", 5, 2029),
    Book(4, "HP1", "Author 1", "Book Description", 2, 2028),
    Book(5, "HP2", "Author 2", "Book Description", 3, 2027),
    Book(6, "HP3", "Author 3", "Book Description", 1, 2026),
]


def find_book_id(book: Book) -> Book:
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.get("/books")
async def read_all_books():
    # FastAPI will by default try to serialize attributes of simple objects
    return BOOKS  # [web:12]


@app.post("/create_book")
async def create_book(book_request: BookRequest):
    # Ignore incoming ID on create, rely on in‑memory auto-increment
    new_book = Book(**book_request.model_dump())
    new_book = find_book_id(new_book)
    BOOKS.append(new_book)
    return new_book  # [web:10][web:12]
