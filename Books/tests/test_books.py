from fastapi.testclient import TestClient

from Books.main import app, reset_books, INITIAL_BOOKS

client = TestClient(app)
BOOKS = INITIAL_BOOKS


def test_read_all_books():
    reset_books()
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == BOOKS


def test_read_single_book_found():
    reset_books()
    response = client.get("/books/Title One")
    assert response.status_code == 200
    assert response.json() == {
        "title": "Title One",
        "author": "Author One",
        "category": "science",
    }


def test_read_single_book_not_found():
    reset_books()
    response = client.get("/books/Nonexistent")
    assert response.status_code == 200
    assert response.json() is None


def test_read_books_by_category_science():
    reset_books()
    response = client.get("/books/", params={"category": "science"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(book["category"].lower() == "science" for book in data)


def test_read_books_by_category_case_insensitive():
    reset_books()
    response = client.get("/books/", params={"category": "ScIeNcE"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(book["category"].lower() == "science" for book in data)


def test_read_books_by_author_and_category():
    reset_books()
    response = client.get("/books/author/Author Two", params={"category": "math"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["author"] == "Author Two"
    assert data[0]["category"] == "math"


def test_update_book_replaces_existing():
    reset_books()
    updated = {
        "title": "Title One",
        "author": "New Author",
        "category": "New Category",
    }
    response = client.put("/books/update_book", json=updated)
    assert response.status_code == 200 or response.status_code == 204

    response_all = client.get("/books")
    assert response_all.status_code == 200
    data = response_all.json()
    matches = [b for b in data if b["title"] == "Title One"]
    assert len(matches) == 1
    assert matches[0]["author"] == "New Author"
    assert matches[0]["category"] == "New Category"


def test_delete_book_removes_from_list():
    reset_books()
    response_before = client.get("/books/Title Two")
    assert response_before.status_code == 200
    assert response_before.json() is not None

    response = client.delete("/books/delete_book/Title Two")
    assert response.status_code == 200 or response.status_code == 204

    response_after = client.get("/books/Title Two")
    assert response_after.status_code == 200
    assert response_after.json() is None


def test_fetch_author_books_returns_all_matching():
    reset_books()
    response = client.get("/books/author_books/Author Two")
    assert response.status_code == 200
    data = response.json()
    # With your initial BOOKS, Author Two has two books
    assert len(data) == 2
    assert all(book["author"] == "Author Two" for book in data)
