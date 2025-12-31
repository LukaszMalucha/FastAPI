from fastapi.testclient import TestClient
from Books_Api.main import app, BOOKS

client = TestClient(app)


def test_read_book_by_id_success():
    # Use an existing book id
    book_id = BOOKS[0].id
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == BOOKS[0].title


def test_read_book_by_id_not_found():
    # Use an id larger than any existing
    missing_id = max(b.id for b in BOOKS) + 1000
    response = client.get(f"/books/{missing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_read_book_by_id_invalid_path_param():
    # id <= 0 should fail path validation
    response = client.get("/books/0")
    assert response.status_code == 422


def test_read_books_by_rating_match():
    # Use rating value that exists
    rating = BOOKS[0].rating
    response = client.get(f"/books/?book_rating={rating}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(item["rating"] == rating for item in data)


def test_read_books_by_rating_no_match():
    # Use rating that does not exist but still valid
    existing_ratings = {b.rating for b in BOOKS}
    candidate = 1
    while candidate in existing_ratings and candidate <= 5:
        candidate += 1
    # If all 1-5 exist, just pick 5 and delete/assert differently
    rating = candidate if candidate <= 5 else 5

    response = client.get(f"/books/?book_rating={rating}")
    assert response.status_code == 200
    data = response.json()
    if rating in existing_ratings:
        # some will exist
        assert all(item["rating"] == rating for item in data)
    else:
        # none should exist
        assert data == []


def test_read_books_by_rating_invalid_query_param():
    # rating >= 6 should fail query validation
    response = client.get("/books/?book_rating=6")
    assert response.status_code == 422


def test_read_books_by_publish_date_match():
    published_date = BOOKS[0].published_date
    response = client.get(f"/books/publish/?published_date={published_date}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(item["published_date"] == published_date for item in data)


def test_read_books_by_publish_date_no_match():
    # Find a valid year that is not used
    used_years = {b.published_date for b in BOOKS}
    year = 2001
    while year in used_years and year < 2099:
        year += 1

    response = client.get(f"/books/publish/?published_date={year}")
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_read_books_by_publish_date_invalid_query_param():
    # year outside allowed range -> validation error
    response_low = client.get("/books/publish/?published_date=1800")
    response_high = client.get("/books/publish/?published_date=2200")
    assert response_low.status_code == 422
    assert response_high.status_code == 422


def test_update_book_success():
    # Create a book first to have a known id
    new_book = {
        "title": "Updatable Book",
        "author": "Updater",
        "description": "To be updated",
        "rating": 3,
        "published_date": 2035,
    }
    create_resp = client.post("/create_book", json=new_book)
    created = create_resp.json()
    book_id = created["id"]

    updated_payload = {
        "id": book_id,
        "title": "Updated Title",
        "author": "Updated Author",
        "description": "Updated description",
        "rating": 5,
        "published_date": 2036,
    }

    resp = client.put("/books/update_book", json=updated_payload)
    # Endpoint returns 204 with no body on success
    assert resp.status_code == 204

    # Verify in-memory state actually changed
    get_resp = client.get(f"/books/{book_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["title"] == "Updated Title"
    assert data["author"] == "Updated Author"
    assert data["rating"] == 5
    assert data["published_date"] == 2036


def test_update_book_not_found():
    # Use a non-existent id
    missing_id = max(b.id for b in BOOKS) + 1000
    payload = {
        "id": missing_id,
        "title": "Does Not Matter",
        "author": "Nobody",
        "description": "No description",
        "rating": 3,
        "published_date": 2030,
    }
    resp = client.put("/books/update_book", json=payload)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Item not found"


def test_update_book_validation_error():
    # invalid rating and missing title
    bad_payload = {
        "id": BOOKS[0].id,
        "author": "Bad Author",
        "description": "Bad",
        "rating": 10,
        "published_date": 2030,
    }
    resp = client.put("/books/update_book", json=bad_payload)
    assert resp.status_code == 422


def test_delete_book_success():
    # Create a book and then delete it
    new_book = {
        "title": "Delete Me",
        "author": "Deleter",
        "description": "To be deleted",
        "rating": 2,
        "published_date": 2033,
    }
    create_resp = client.post("/create_book", json=new_book)
    created = create_resp.json()
    book_id = created["id"]

    # Delete
    delete_resp = client.delete(f"/books/{book_id}")
    assert delete_resp.status_code == 204

    # Verify it is gone
    get_resp = client.get(f"/books/{book_id}")
    assert get_resp.status_code == 404


def test_delete_book_not_found():
    missing_id = max(b.id for b in BOOKS) + 1000
    delete_resp = client.delete(f"/books/{missing_id}")
    assert delete_resp.status_code == 404
    assert delete_resp.json()["detail"] == "Item not found"


def test_delete_book_invalid_path_param():
    resp = client.delete("/books/0")
    assert resp.status_code == 422
