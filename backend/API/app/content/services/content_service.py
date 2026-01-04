from app.auth.models.nn_user import NNUser
from app.content.models.content import Content, CreateContent
from app.content.repositories.content_repository import ContentRepository
from app.content.services.embroidery_service import EmbroideryService


class ContentService:
    def __init__(
        self,
        repo: ContentRepository,
        embroidery_service: EmbroideryService,
    ):
        self.repo = repo
        self.embroidery_service = embroidery_service

    async def save_content(self, content: CreateContent, user: NNUser):
        content_to_save = Content(user_id=user.id, **content.model_dump())
        saved_content = await self.repo.create(content_to_save)

        return saved_content
