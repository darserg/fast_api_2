from pydantic import BaseModel, Field


class PresignUploadRequest(BaseModel):
    object_name: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=255)
    folder: str = Field(default="uploads", min_length=1, max_length=255)


class PresignUploadResponse(BaseModel):
    key: str
    upload_url: str
    public_url: str
