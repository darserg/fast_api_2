from dataclasses import dataclass
from typing import Protocol

from src.core.config import settings


@dataclass(slots=True)
class PresignedUpload:
    key: str
    upload_url: str
    public_url: str


class StorageService(Protocol):
    def build_public_url(self, key: str) -> str: ...

    def generate_presigned_upload(self, key: str, content_type: str) -> PresignedUpload: ...


class DummyStorageService:
    def build_public_url(self, key: str) -> str:
        base = settings.S3_PUBLIC_BASE_URL.rstrip("/")
        return f"{base}/{key}" if base else key

    def generate_presigned_upload(self, key: str, content_type: str) -> PresignedUpload:
        public_url = self.build_public_url(key)
        return PresignedUpload(
            key=key,
            upload_url=public_url,
            public_url=public_url,
        )


class S3StorageService(DummyStorageService):
    def __init__(self) -> None:
        import boto3

        client_kwargs = {
            "service_name": "s3",
            "endpoint_url": settings.S3_ENDPOINT_URL,
            "aws_access_key_id": settings.S3_ACCESS_KEY,
            "aws_secret_access_key": settings.S3_SECRET_KEY,
            "region_name": settings.S3_REGION,
        }
        self._client = boto3.client(**client_kwargs)

    def generate_presigned_upload(self, key: str, content_type: str) -> PresignedUpload:
        upload_url = self._client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.S3_BUCKET_NAME,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=settings.S3_PRESIGNED_EXPIRES_SECONDS,
        )
        return PresignedUpload(
            key=key,
            upload_url=upload_url,
            public_url=self.build_public_url(key),
        )


def get_storage_service() -> StorageService:
    if settings.S3_ENABLED:
        return S3StorageService()
    return DummyStorageService()
