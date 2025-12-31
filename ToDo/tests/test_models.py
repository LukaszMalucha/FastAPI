from ToDo.database import Base
from ToDo.models import Users, Todos

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# In-memory SQLite with foreign keys enabled
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """Create test engine with foreign keys enabled."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Provide a transactional session per test with foreign keys."""
    connection = engine.connect()
    # Use text() wrapper for PRAGMA in SQLAlchemy 2.0+
    connection.execute(text("PRAGMA foreign_keys=ON"))
    connection.commit()  # Commit PRAGMA changes

    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# All your test functions remain identical...
def test_users_create_valid_user(db_session):
    """Test creating a valid Users instance."""
    user = Users(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        hashed_password="hashedpass123",
        is_active=True,
        role="user"
    )
    db_session.add(user)
    db_session.commit()

    saved_user = db_session.query(Users).filter_by(username="testuser").first()
    assert saved_user.email == "test@example.com"
    assert saved_user.is_active is True
    assert saved_user.role == "user"


def test_users_unique_constraints(db_session):
    """Test unique constraints on email and username."""
    user1 = Users(email="unique@example.com", username="uniqueuser",
                  first_name="Test", last_name="User", hashed_password="pass")
    db_session.add(user1)
    db_session.commit()

    user2 = Users(email="unique@example.com", username="differentuser",
                  first_name="Test2", last_name="User2", hashed_password="pass")
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_users_default_is_active(db_session):
    """Test default value for is_active."""
    user = Users(
        email="active@example.com",
        username="activeuser",
        first_name="Active",
        last_name="User",
        hashed_password="pass"
    )
    db_session.add(user)
    db_session.commit()
    assert user.is_active is True


def test_todos_create_valid_todo(db_session):
    """Test creating a valid Todos instance with owner."""
    owner = Users(
        email="owner@example.com",
        username="owner",
        first_name="Owner",
        last_name="User",
        hashed_password="pass"
    )
    db_session.add(owner)
    db_session.commit()

    todo = Todos(
        title="Test Todo",
        description="Test description",
        priority=5,
        complete=False,
        owner_id=owner.id
    )
    db_session.add(todo)
    db_session.commit()

    saved_todo = db_session.query(Todos).filter_by(title="Test Todo").first()
    assert saved_todo.description == "Test description"
    assert saved_todo.priority == 5
    assert saved_todo.complete is False
    assert saved_todo.owner_id == owner.id


def test_todos_default_complete(db_session):
    """Test default value for complete."""
    owner = Users(email="test@example.com", username="test",
                  first_name="T", last_name="U", hashed_password="pass")
    db_session.add(owner)
    db_session.commit()

    todo = Todos(title="Default Todo", owner_id=owner.id)
    db_session.add(todo)
    db_session.commit()
    assert todo.complete is False


def test_todos_invalid_owner_id(db_session):
    """Test foreign key constraint violation."""
    todo = Todos(title="Invalid Todo", owner_id=999)
    db_session.add(todo)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_relationship_query(db_session):
    """Test querying todos by owner."""
    owner = Users(email="multi@example.com", username="multi",
                  first_name="Multi", last_name="User", hashed_password="pass")
    db_session.add(owner)
    db_session.commit()

    todo1 = Todos(title="Todo 1", owner_id=owner.id)
    todo2 = Todos(title="Todo 2", owner_id=owner.id)
    db_session.add_all([todo1, todo2])
    db_session.commit()

    owner_todos = db_session.query(Todos).filter_by(owner_id=owner.id).all()
    assert len(owner_todos) == 2
    assert any(todo.title == "Todo 1" for todo in owner_todos)


def test_full_user_todo_workflow(db_session):
    """Test complete workflow: create user, create todos, query relationship."""
    user = Users(
        email="workflow@example.com",
        username="workflow",
        first_name="Workflow",
        last_name="User",
        hashed_password="securepass"
    )
    db_session.add(user)
    db_session.commit()

    todos = [
        Todos(title="High Priority", priority=10, owner_id=user.id),
        Todos(title="Low Priority", priority=1, owner_id=user.id)
    ]
    db_session.add_all(todos)
    db_session.commit()

    saved_user = db_session.query(Users).filter_by(username="workflow").first()
    user_todos = db_session.query(Todos).filter_by(owner_id=saved_user.id).all()

    assert len(user_todos) == 2
    priorities = [todo.priority for todo in user_todos]
    assert 10 in priorities and 1 in priorities
