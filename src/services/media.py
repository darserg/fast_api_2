import uuid

from src.core.storage import PresignedUpload, StorageService


class MediaService:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage

    def create_presigned_upload(
        self,
        *,
        object_name: str,
        content_type: str,
        folder: str,
    ) -> PresignedUpload:
        key = f"{folder.rstrip('/')}/{uuid.uuid4()}-{object_name}"
        return self.storage.generate_presigned_upload(key, content_type)

    def build_image_payloads(self, keys: list[str]) -> list[dict[str, str]]:
        return [
            {
                "file_key": key,
                "file_url": self.storage.build_public_url(key),
            }
            for key in keys
        ]
