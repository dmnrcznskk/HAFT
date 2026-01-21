import pytest
from httpx import AsyncClient, ASGITransport
from app.main import api
from app.auth.services.auth_service import AuthService
from app.core.dependencies import get_auth_service, get_current_user
from unittest.mock import AsyncMock, MagicMock
from app.auth.models.nn_user import NNUser, ResponseNNUser
from app.auth.models.token import Token
import uuid

@pytest.fixture
def mock_auth_service():
    service = AsyncMock(spec=AuthService)
    return service

@pytest.fixture
def mock_user():
    return NNUser(id=uuid.uuid4(), email="test@example.com", hashed_password="hashed")

@pytest.mark.anyio
async def test_register_endpoint(mock_auth_service):
    api.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.post("/auth/register/", json={"email": "test@example.com", "password": "password123"})
    
    assert response.status_code == 201
    assert response.json() == {"message": "User created successfully"}
    mock_auth_service.register_user.assert_called_once()
    
    api.dependency_overrides.clear()

@pytest.mark.anyio
async def test_login_endpoint(mock_auth_service):
    api.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    
    access_token = Token(token_value="access_val", token_type="access")
    refresh_token = Token(token_value="refresh_val", token_type="refresh")
    mock_auth_service.login_user.return_value = (access_token, refresh_token)
    
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.post("/auth/token/", data={"username": "test@example.com", "password": "password123"})
    
    assert response.status_code == 200
    assert response.json() == {"access_token": "access_val", "token_type": "bearer"}
    assert "refresh_token" in response.cookies
    
    api.dependency_overrides.clear()

@pytest.mark.anyio
async def test_get_profile_me(mock_user):
    api.dependency_overrides[get_current_user] = lambda: mock_user
    
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get("/auth/profile/me")
    
    assert response.status_code == 200
    assert response.json()["email"] == mock_user.email
    assert response.json()["id"] == str(mock_user.id)
    
    api.dependency_overrides.clear()
