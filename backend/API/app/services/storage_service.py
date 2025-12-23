from fastapi import UploadFile, File
from storage3.types import FileOptions
from supabase import Client, create_client

from app.core.config import settings
from app.models.bucket import Bucket


class StorageService:
    def __init__(self):
        self.supabase_client: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    async def save_img(
        self, path: str, bucket: Bucket, file: UploadFile = File(...)
    ) -> str:
        try:
            file_content = await file.read()
            if not file_content:
                raise ValueError("File is empty")

            options: FileOptions = {"content-type": file.content_type}

            self.supabase_client.storage.from_(bucket.value).upload(
                path=path, file=file_content, file_options=options
            )
            public_url = self.supabase_client.storage.from_(
                bucket.value
            ).get_public_url(path)

            return public_url

        except Exception as e:
            print(e)
