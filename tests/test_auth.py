"""
Authentication tests for the Task Management API.
Tests user registration, login, and token validation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from config.config import Base, get_db
from app.models.user import User
from app.services.auth_service import AuthService

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

class TestAuthentication:
    """Test suite for authentication endpoints."""

    def test_register_user(self):
        """Test user registration with valid data."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123!",
                "full_name": "Test User"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert "id" in data
        assert data["is_active"] == True
        assert data["is_admin"] == False

    def test_register_duplicate_username(self):
        """Test registration with duplicate username."""
        # First registration
        client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test1@example.com",
                "password": "TestPass123!"
            }
        )

        # Second registration with same username
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test2@example.com",
                "password": "TestPass123!"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_invalid_email(self):
        """Test registration with invalid email format."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "invalidemail",
                "password": "TestPass123!"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_register_weak_password(self):
        """Test registration with weak password."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "weak"
            }
        )

        assert response.status_code == 400
        assert "Password must be at least 8 characters" in response.json()["detail"]

    def test_login_success(self):
        """Test successful login."""
        # Register user first
        client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123!"
            }
        )

        # Login
        response = client.post(
            "/api/auth/login",
            data={
                "username": "testuser",
                "password": "TestPass123!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        """Test login with wrong password."""
        # Register user first
        client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123!"
            }
        )

        # Login with wrong password
        response = client.post(
            "/api/auth/login",
            data={
                "username": "testuser",
                "password": "WrongPass123!"
            }
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self):
        """Test login with non-existent user."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent",
                "password": "TestPass123!"
            }
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]