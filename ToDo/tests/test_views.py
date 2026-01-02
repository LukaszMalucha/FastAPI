import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker
from ToDo.main import get_db, app
from ToDo import models

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def client():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=pool.StaticPool
    )
    models.Base.metadata.create_all(bind=engine)
    SessionTesting = sessionmaker(bind=engine)

    def override_get_db():
        db = SessionTesting()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    models.Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

# Your existing tests here...

@pytest.fixture
def todo_data():
    return {
        "title": "Test Todo",
        "description": "Test Description",
        "priority": 1,
        "complete": False
    }

def test_create_todo_success(client: TestClient, todo_data):
    response = client.post("/todo", json=todo_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Todo"
    assert "id" in data  # Should have ID after creation

def test_create_todo_missing_title(client: TestClient):
    data = {"description": "Test", "priority": 1, "complete": False}
    response = client.post("/todo", json=data)
    assert response.status_code == 422

def test_update_todo_not_found(client: TestClient):
    # Use valid data that passes Pydantic validation
    data = {
        "title": "Valid Title",
        "description": "Valid description",  # Non-empty
        "priority": 2,
        "complete": True
    }
    response = client.put("/todo/999", json=data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found."


def test_update_todo_success(client: TestClient, todo_data):
    # Create todo
    create_response = client.post("/todo", json=todo_data)
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    # Update
    update_data = {"title": "Updated", "description": "New desc", "priority": 3, "complete": True}
    response = client.put(f"/todo/{todo_id}", json=update_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify
    get_response = client.get(f"/todo/{todo_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["title"] == "Updated"
    assert data["complete"] is True
