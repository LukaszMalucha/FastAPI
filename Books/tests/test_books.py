# tests/test_main.py
from fastapi.testclient import TestClient

from books import app

BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'},
]

client = TestClient(app)


def test_read_all_books():
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == BOOKS


def test_read_single_book_found():
    response = client.get("/books/Title One")
    assert response.status_code == 200
    assert response.json() == {
        "title": "Title One",
        "author": "Author One",
        "category": "science",
    }


def test_read_single_book_not_found():
    response = client.get("/books/Nonexistent")
    # current implementation returns 200 with null body if not found;
    # adjust expected behaviour if you later raise HTTPException instead
    assert response.status_code == 200
    assert response.json() is None


def test_read_books_by_category_science():
    response = client.get("/books/", params={"category": "science"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(book["category"].lower() == "science" for book in data)


def test_read_books_by_category_case_insensitive():
    response = client.get("/books/", params={"category": "ScIeNcE"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(book["category"].lower() == "science" for book in data)


def test_read_books_by_author_and_category():
    response = client.get("/books/author/Author Two", params={"category": "math"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["author"] == "Author Two"
    assert data[0]["category"] == "math"
