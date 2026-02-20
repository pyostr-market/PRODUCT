import asyncio
import mimetypes
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

import boto3


class ImageStorageService(ABC):

    @abstractmethod
    async def upload_bytes(self, *, data: bytes, key: str, content_type: str | None = None) -> None:
        ...

    @abstractmethod
    async def delete_object(self, key: str) -> None:
        ...

    @abstractmethod
    def build_key(self, *, folder: str, filename: str) -> str:
        ...

    @abstractmethod
    def build_public_url(self, key: str) -> str:
        ...


class S3ImageStorageService(ImageStorageService):

    def __init__(
        self,
        *,
        bucket_name: str,
        access_key: str,
        secret_access_key: str,
        endpoint_url: str,
        region_name: str,
    ):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url.rstrip("/")
        self.client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key,
            endpoint_url=self.endpoint_url,
            region_name=region_name,
        )

    @classmethod
    def from_settings(cls):
        from src.core.conf.settings import get_settings

        settings = get_settings()
        return cls(
            bucket_name=settings.BUCKET_NAME,
            access_key=settings.S3_ACCESS_KEY,
            secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            endpoint_url=settings.S3_URL,
            region_name=settings.S3_REGION,
        )

    async def upload_bytes(self, *, data: bytes, key: str, content_type: str | None = None) -> None:
        extra_args: dict[str, str] = {}
        if content_type:
            extra_args["ContentType"] = content_type

        await asyncio.to_thread(
            self.client.put_object,
            Bucket=self.bucket_name,
            Key=key,
            Body=data,
            **extra_args,
        )

    async def delete_object(self, key: str) -> None:
        await asyncio.to_thread(
            self.client.delete_object,
            Bucket=self.bucket_name,
            Key=key,
        )

    def build_key(self, *, folder: str, filename: str) -> str:
        ext = Path(filename or "test.img").suffix or ".img"
        return f"{folder.strip('/')}/{uuid.uuid4()}{ext}"

    def build_public_url(self, key: str) -> str:
        return f"{self.endpoint_url}/{self.bucket_name}/{key}"



def guess_content_type(filename: str) -> str:
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or "application/octet-stream"
