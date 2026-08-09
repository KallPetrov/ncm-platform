import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.core.security import create_access_token, verify_password, get_password_hash
import bcrypt


@pytest.fixture
def db_session():
    """Create a test database session"""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session: Session):
    """Create an admin user"""
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin"),
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_password_hashing(self):
        """Test that password hashing works correctly"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_password_verification(self):
        """Test that password verification works correctly"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
    
    def test_bcrypt_hashing(self):
        """Test direct bcrypt hashing"""
        password = "test_password_123"
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        assert bcrypt.checkpw(password.encode('utf-8'), hashed) is True
        assert bcrypt.checkpw(b"wrong_password", hashed) is False


@pytest.mark.unit
@pytest.mark.auth
class TestJWTToken:
    """Test JWT token functionality"""
    
    def test_token_creation(self):
        """Test that JWT token creation works"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_token_structure(self):
        """Test that JWT token has correct structure"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # JWT tokens have 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3
    
    def test_token_with_expiration(self):
        """Test that JWT token includes expiration"""
        from app.core.security import decode_access_token
        from datetime import timedelta
        
        data = {"sub": "testuser"}
        token = create_access_token(data, expires_delta=timedelta(minutes=30))
        
        payload = decode_access_token(token)
        assert payload is not None
        assert "exp" in payload
        assert payload["sub"] == "testuser"


@pytest.mark.unit
@pytest.mark.auth
class TestAuthenticationEndpoints:
    """Test authentication API endpoints"""
    
    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login"""
        response = client.post(
            "/auth/login",
            data={"username": "testuser", "password": "testpassword"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials"""
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
    
    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing fields"""
        response = client.post(
            "/auth/login",
            data={"username": "testuser"}
        )
        
        assert response.status_code == 422
    
    def test_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token"""
        response = client.get("/users/me")
        
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_token(self, client: TestClient, test_user: User):
        """Test accessing protected endpoint with valid token"""
        # First login to get token
        login_response = client.post(
            "/auth/login",
            data={"username": "testuser", "password": "testpassword"}
        )
        token = login_response.json()["access_token"]
        
        # Access protected endpoint
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    def test_protected_endpoint_with_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token"""
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.auth
class TestUserManagement:
    """Test user management endpoints"""
    
    def test_create_user(self, client: TestClient, admin_user: User):
        """Test creating a new user"""
        # Login as admin
        login_response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"}
        )
        token = login_response.json()["access_token"]
        
        # Create new user
        response = client.post(
            "/users/",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpassword123"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
    
    def test_list_users(self, client: TestClient, admin_user: User):
        """Test listing all users"""
        # Login as admin
        login_response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"}
        )
        token = login_response.json()["access_token"]
        
        # List users
        response = client.get(
            "/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_current_user(self, client: TestClient, test_user: User):
        """Test getting current user info"""
        # Login
        login_response = client.post(
            "/auth/login",
            data={"username": "testuser", "password": "testpassword"}
        )
        token = login_response.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
