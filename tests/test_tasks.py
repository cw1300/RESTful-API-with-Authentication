"""
Task tests for the Task Management API.
Tests CRUD operations for tasks.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

from main import app
from config.config import Base, get_db
from app.models.task import TaskStatus, TaskPriority

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_token():
    """Get authentication token for testing."""
    # Register a test user
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        }
    )

    # Login to get token
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "TestPass123!"
        }
    )

    return response.json()["access_token"]

class TestTasks:
    """Test suite for task endpoints."""

    def test_create_task(self, auth_token):
        """Test creating a new task."""
        response = client.post(
            "/api/tasks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "title": "Test Task",
                "description": "This is a test task",
                "priority": "high",
                "due_date": (datetime.now() + timedelta(days=7)).isoformat()
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "This is a test task"
        assert data["priority"] == "high"
        assert data["status"] == "todo"
        assert "id" in data

    def test_create_task_unauthorized(self):
        """Test creating a task without authentication."""
        response = client.post(
            "/api/tasks/",
            json={
                "title": "Test Task",
                "description": "This is a test task"
            }
        )

        assert response.status_code == 401

    def test_get_tasks(self, auth_token):
        """Test getting all tasks for a user."""
        # Create some tasks first
        for i in range(3):
            client.post(
                "/api/tasks/",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "title": f"Test Task {i}",
                    "description": f"Description {i}",
                    "priority": "medium"
                }
            )

        # Get all tasks
        response = client.get(
            "/api/tasks/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("Test Task" in task["title"] for task in data)

    def test_get_task_by_id(self, auth_token):
        """Test getting a specific task by ID."""
        # Create a task
        create_response = client.post(
            "/api/tasks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "title": "Specific Task",
                "description": "Task to fetch by ID"
            }
        )
        task_id = create_response.json()["id"]

        # Get the task
        response = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Specific Task"
        assert data["id"] == task_id

    def test_update_task(self, auth_token):
        """Test updating a task."""
        # Create a task
        create_response = client.post(
            "/api/tasks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "title": "Task to Update",
                "status": "todo"
            }
        )
        task_id = create_response.json()["id"]

        # Update the task
        response = client.put(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "title": "Updated Task",
                "status": "in_progress",
                "priority": "high"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["status"] == "in_progress"
        assert data["priority"] == "high"

    def test_delete_task(self, auth_token):
        """Test deleting a task."""
        # Create a task
        create_response = client.post(
            "/api/tasks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "title": "Task to Delete"
            }
        )
        task_id = create_response.json()["id"]

        # Delete the task
        response = client.delete(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 204

        # Verify task is deleted
        get_response = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert get_response.status_code == 404

    def test_filter_tasks_by_status(self, auth_token):
        """Test filtering tasks by status."""
        # Create tasks with different statuses
        statuses = ["todo", "in_progress", "completed"]
        for status in statuses:
            client.post(
                "/api/tasks/",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "title": f"Task {status}",
                    "status": status
                }
            )

        # Filter by status
        response = client.get(
            "/api/tasks/?status=in_progress",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "in_progress"