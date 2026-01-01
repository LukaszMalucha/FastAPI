import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker
from ToDo.main import get_db
from ToDo import models
from ToDo.main import app

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
    app.dependency_overrides.clear()


def test_read_all_empty(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == []


def test_read_todo_not_found(client: TestClient):
    response = client.get("/todo/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found."


def test_read_todo_success(client: TestClient):
    # Create test todo first
    db = next(client.app.dependency_overrides[get_db]())
    todo = models.Todos(title="Test Todo", description="Test Description", priority=1, complete=False)
    db.add(todo)
    db.commit()
    db.refresh(todo)

    response = client.get(f"/todo/{todo.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Todo"


def test_read_all_multiple_todos(client: TestClient):
    # Create multiple todos
    db = next(client.app.dependency_overrides[get_db]())
    todo1 = models.Todos(title="Todo 1", description="Desc 1", priority=1)
    todo2 = models.Todos(title="Todo 2", description="Desc 2", priority=2)
    db.add_all([todo1, todo2])
    db.commit()

    response = client.get("/")
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 2
    assert todos[0]["title"] == "Todo 1"
    assert todos[1]["title"] == "Todo 2"
