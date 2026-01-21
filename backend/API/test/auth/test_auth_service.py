import pytest
from unittest.mock import AsyncMock, MagicMock
from app.auth.services.auth_service import AuthService
from app.auth.models.nn_user import CreateNNUser, NNUser, UpdateNNUser
from fastapi import HTTPException
import app.core.security as security

@pytest.fixture
def user_repo():
    return AsyncMock()

@pytest.fixture
def auth_service(user_repo):
    return AuthService(repo=user_repo)

@pytest.mark.anyio
async def test_register_user_success(auth_service, user_repo):
    new_user_data = CreateNNUser(email="test@example.com", password="password123", username="testuser")
    user_repo.get_user_by_email.return_value = None
    user_repo.create.side_effect = lambda x: x

    result = await auth_service.register_user(new_user_data)

    assert result.email == "test@example.com"
    assert result.username == "testuser"
    assert hasattr(result, "hashed_password")
    user_repo.get_user_by_email.assert_called_once_with("test@example.com")
    user_repo.create.assert_called_once()

@pytest.mark.anyio
async def test_register_user_already_exists(auth_service, user_repo):
    new_user_data = CreateNNUser(email="test@example.com", password="password123")
    user_repo.get_user_by_email.return_value = NNUser(email="test@example.com", hashed_password="hashed")

    with pytest.raises(HTTPException) as excinfo:
        await auth_service.register_user(new_user_data)
    
    assert excinfo.value.status_code == 400
    assert "already exists" in excinfo.value.detail

@pytest.mark.anyio
async def test_login_user_success(auth_service, user_repo, monkeypatch):
    email = "test@example.com"
    password = "password123"
    hashed_password = auth_service.password_hash.hash(password)
    user = NNUser(email=email, hashed_password=hashed_password)
    
    user_repo.get_user_by_email.return_value = user
    
    # Mock security.create_token
    mock_create_token = MagicMock(return_value="mock_token")
    monkeypatch.setattr(security, "create_token", mock_create_token)

    access_token, refresh_token = await auth_service.login_user(email, password)

    assert access_token.token_value == "mock_token"
    assert refresh_token.token_value == "mock_token"
    assert access_token.token_type == "access"
    assert refresh_token.token_type == "refresh"

@pytest.mark.anyio
async def test_login_user_invalid_credentials(auth_service, user_repo):
    user_repo.get_user_by_email.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await auth_service.login_user("wrong@example.com", "wrong")
    
    assert excinfo.value.status_code == 401
    assert "Incorrect email or password" in excinfo.value.detail

@pytest.mark.anyio
async def test_get_user_from_token_success(auth_service, user_repo, monkeypatch):
    token = "valid_token"
    email = "test@example.com"
    user = NNUser(email=email, hashed_password="hashed")
    
    monkeypatch.setattr(security, "get_payload", lambda t, e: {"sub": email})
    user_repo.get_user_by_email.return_value = user

    result = await auth_service.get_user_from_token(token)

    assert result == user
    user_repo.get_user_by_email.assert_called_once_with(email)

@pytest.mark.anyio
async def test_update_user_profile(auth_service, user_repo):
    user = NNUser(email="old@example.com", hashed_password="old_hashed", username="olduser")
    update_data = UpdateNNUser(username="newuser", password="newpassword")
    
    user_repo.update_db_user.side_effect = lambda u, d: u
    
    await auth_service.update_user_profile(update_data, user)
    
    user_repo.update_db_user.assert_called_once()
    args, _ = user_repo.update_db_user.call_args
    assert args[1]["username"] == "newuser"
    assert "hashed_password" in args[1]
