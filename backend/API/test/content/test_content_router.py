import pytest
from httpx import AsyncClient, ASGITransport
from app.main import api
from app.content.services.content_service import ContentService
from app.core.dependencies import get_content_service, get_current_user
from unittest.mock import AsyncMock
from app.auth.models.nn_user import NNUser
from app.content.models.content import Content
from app.content.models.content_type import ContentType
import uuid

@pytest.fixture
def mock_content_service():
    return AsyncMock(spec=ContentService)

@pytest.fixture
def mock_user():
    return NNUser(id=uuid.uuid4(), email="test@example.com", hashed_password="hashed")

@pytest.mark.anyio
async def test_create_content_endpoint(mock_content_service, mock_user):
    api.dependency_overrides[get_content_service] = lambda: mock_content_service
    api.dependency_overrides[get_current_user] = lambda: mock_user
    
    content_id = uuid.uuid4()
    mock_content_service.save_content.return_value = Content(
        id=content_id, title="Test", text="Text", content_type=ContentType.embroidery, user_id=mock_user.id
    )
    
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.post("/content/create", json={
            "title": "Test", "text": "Text", "content_type": "embroidery"
        })
    
    assert response.status_code == 200
    assert response.json()["title"] == "Test"
    mock_content_service.save_content.assert_called_once()
    
    api.dependency_overrides.clear()

@pytest.mark.anyio
async def test_get_public_library_endpoint(mock_content_service):
    api.dependency_overrides[get_content_service] = lambda: mock_content_service
    mock_content_service.get_public_embroideries.return_value = []
    
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get("/content/library/public")
    
    assert response.status_code == 200
    assert response.json() == []
    mock_content_service.get_public_embroideries.assert_called_once()
    
    api.dependency_overrides.clear()

@pytest.mark.anyio
async def test_create_embroidery_endpoint(mock_content_service, mock_user):
    api.dependency_overrides[get_content_service] = lambda: mock_content_service
    api.dependency_overrides[get_current_user] = lambda: mock_user
    
    content_id = uuid.uuid4()
    mock_content_service.save_embroidery.return_value = {"id": 1, "url": "http://test.com/img.png"}
    
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        files = {"file": ("test.png", b"fake-image-content", "image/png")}
        response = await ac.post(f"/content/{content_id}/embroidery/", files=files)
    
    assert response.status_code == 200
    assert response.json()["url"] == "http://test.com/img.png"
    mock_content_service.save_embroidery.assert_called_once()
    
    api.dependency_overrides.clear()

@pytest.mark.anyio
async def test_get_embroidery_endpoint(mock_content_service, mock_user):
    api.dependency_overrides[get_content_service] = lambda: mock_content_service
    api.dependency_overrides[get_current_user] = lambda: mock_user
    
    content_id = uuid.uuid4()
    mock_content_service.get_embroidery_by_content_id.return_value = {
        "id": str(content_id), "url": "http://test.com/img.png", "title": "Test", "text": "Text", "content_type": "embroidery"
    }
    
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get(f"/content/{content_id}/embroidery/")
    
    assert response.status_code == 200
    assert response.json()["url"] == "http://test.com/img.png"
    mock_content_service.get_embroidery_by_content_id.assert_called_once()
    
    api.dependency_overrides.clear()

@pytest.mark.anyio
async def test_get_private_library_endpoint(mock_content_service, mock_user):
    api.dependency_overrides[get_content_service] = lambda: mock_content_service
    api.dependency_overrides[get_current_user] = lambda: mock_user
    
    mock_content_service.get_private_library.return_value = []
    
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get("/content/library/private")
    
    assert response.status_code == 200
    assert response.json() == []
    mock_content_service.get_private_library.assert_called_once()
    
    api.dependency_overrides.clear()

@pytest.mark.anyio
async def test_get_public_embroideries_of_user_endpoint(mock_content_service):
    api.dependency_overrides[get_content_service] = lambda: mock_content_service
    
    user_id = uuid.uuid4()
    mock_content_service.get_public_embroideries_of_user.return_value = []
    
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get(f"/content/library/public/user/{user_id}")
    
    assert response.status_code == 200
    assert response.json() == []
    mock_content_service.get_public_embroideries_of_user.assert_called_once_with(user_id)
    
    api.dependency_overrides.clear()

@pytest.mark.anyio
async def test_delete_embroidery_endpoint(mock_content_service, mock_user):
    api.dependency_overrides[get_content_service] = lambda: mock_content_service
    api.dependency_overrides[get_current_user] = lambda: mock_user
    
    content_id = uuid.uuid4()
    mock_content_service.delete_embroidery.return_value = None
    
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.delete(f"/content/{content_id}/embroidery/")
    
    assert response.status_code == 200
    assert response.json() == {"message": "Embroidery deleted"}
    mock_content_service.delete_embroidery.assert_called_once()
    
    api.dependency_overrides.clear()

@pytest.mark.anyio
async def test_generate_embroidery_endpoint(monkeypatch):
    from app.content.routers import content_router
    mock_generate = AsyncMock(return_value={"preview_png": "data:...", "chart_png": "data:..."})
    monkeypatch.setattr(content_router, "generate_embroidery_from_picture", mock_generate)
    
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        files = {"img": ("test.png", b"fake-image-content", "image/png")}
        response = await ac.post("/content/embroidery/generate", 
                                 params={"num_colors": 10, "width_cm": 20, "aida_count": 14},
                                 files=files)
    
    assert response.status_code == 200
    assert "preview_png" in response.json()
    mock_generate.assert_called_once()
