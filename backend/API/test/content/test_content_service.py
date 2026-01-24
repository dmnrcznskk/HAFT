import pytest
from unittest.mock import AsyncMock, MagicMock
from app.content.services.content_service import ContentService
from app.content.models.content import CreateContent, Content
from app.content.models.content_type import ContentType
from app.auth.models.nn_user import NNUser
from fastapi import HTTPException
import uuid

@pytest.fixture
def embroidery_repo():
    return AsyncMock()

@pytest.fixture
def content_repo():
    return AsyncMock()

@pytest.fixture
def storage_service():
    return AsyncMock()

@pytest.fixture
def content_service(embroidery_repo, content_repo, storage_service):
    return ContentService(
        embroidery_repo=embroidery_repo,
        content_repo=content_repo,
        storage_service=storage_service
    )

@pytest.fixture
def mock_user():
    return NNUser(id=uuid.uuid4(), email="test@example.com", hashed_password="hashed")

@pytest.mark.anyio
async def test_save_content(content_service, content_repo, mock_user):
    content_data = CreateContent(title="Test", text="Text", content_type=ContentType.embroidery)
    content_repo.create.side_effect = lambda x: x
    
    result = await content_service.save_content(content_data, mock_user)
    
    assert result.title == "Test"
    assert result.user_id == mock_user.id
    content_repo.create.assert_called_once()

@pytest.mark.anyio
async def test_save_embroidery(content_service, content_repo, embroidery_repo, storage_service, mock_user):
    content_id = uuid.uuid4()
    content = Content(id=content_id, user_id=mock_user.id, title="Test", text="Text", content_type=ContentType.embroidery)
    content_repo.get_content_by_id.return_value = content
    storage_service.save_img.return_value = "http://example.com/img.png"
    embroidery_repo.create.side_effect = lambda x: x
    
    mock_file = MagicMock()
    mock_file.filename = "test.png"
    
    result = await content_service.save_embroidery(content_id, mock_file, mock_user)
    
    assert result.url == "http://example.com/img.png"
    assert result.content_id == content_id
    storage_service.save_img.assert_called_once()
    embroidery_repo.create.assert_called_once()

@pytest.mark.anyio
async def test_get_private_library(content_service, embroidery_repo, mock_user):
    embroidery_repo.get_embroideries_by_user_id.return_value = []
    
    result = await content_service.get_private_library(mock_user)
    
    assert isinstance(result, list)
    embroidery_repo.get_embroideries_by_user_id.assert_called_once_with(mock_user.id)

@pytest.mark.anyio
async def test_get_embroidery_by_content_id_success(content_service, content_repo, mock_user):
    content_id = uuid.uuid4()
    content = Content(id=content_id, user_id=mock_user.id, title="Test", text="Text", content_type=ContentType.embroidery, is_public=True)
    content.embroidery = MagicMock()
    content.embroidery.url = "http://example.com/img.png"
    
    content_repo.get_content_by_id.return_value = content
    
    result = await content_service.get_embroidery_by_content_id(content_id, mock_user)
    
    assert result.url == "http://example.com/img.png"
    content_repo.get_content_by_id.assert_called_once_with(content_id)

@pytest.mark.anyio
async def test_get_embroidery_by_content_id_not_found(content_service, content_repo):
    content_id = uuid.uuid4()
    content_repo.get_content_by_id.return_value = None
    
    with pytest.raises(HTTPException) as excinfo:
        await content_service.get_embroidery_by_content_id(content_id)
    
    assert excinfo.value.status_code == 400
    assert "does not exist" in excinfo.value.detail

@pytest.mark.anyio
async def test_delete_embroidery_success(content_service, content_repo, embroidery_repo, storage_service, mock_user):
    content_id = uuid.uuid4()
    content = Content(id=content_id, user_id=mock_user.id, title="Test", text="Text", content_type=ContentType.embroidery)
    embroidery = MagicMock()
    embroidery.url = "http://example.com/storage/v1/object/public/embroidery/img.png"
    content.embroidery = embroidery
    
    content_repo.get_content_by_id.return_value = content
    storage_service.delete = MagicMock()
    
    await content_service.delete_embroidery(content_id, mock_user)
    
    storage_service.delete.assert_called_once_with(embroidery.url)
    embroidery_repo.delete.assert_called_once_with(embroidery)
    content_repo.delete.assert_called_once_with(content)

@pytest.mark.anyio
async def test_get_public_embroideries(content_service, embroidery_repo):
    embroidery_repo.get_public_embroideries.return_value = []
    
    result = await content_service.get_public_embroideries()
    
    assert isinstance(result, list)
    embroidery_repo.get_public_embroideries.assert_called_once()
