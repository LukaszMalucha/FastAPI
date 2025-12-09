from fastapi.testclient import TestClient
from Books_Api.books import app, BOOKS

client = TestClient(app)


def test_read_all_books_returns_initial_list():
    response = client.get("/books")
    assert response.status_code == 200
    data = response.json()
    # initial list has 6 books
    assert isinstance(data, list)
    assert len(data) == 6


def test_create_book_adds_book_to_list():
    # Arrange
    new_book = {
        "id": 7,
        "title": "New Book",
        "author": "Test Author",
        "description": "Test description",
        "rating": 4,
        "published_date": 2031
    }

    # Act
    response = client.post("/create_book", json=new_book)

    # Assert HTTP response
    assert response.status_code == 200

    # Assert in-memory list was modified
    assert any(b.id == 7 for b in BOOKS)
