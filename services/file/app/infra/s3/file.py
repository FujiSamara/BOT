from mypy_boto3_s3 import ServiceResource

from typing import AsyncContextManager, Callable
from common.contracts.clients import FileClient


class S3FileClient(FileClient):
    def __init__(
        self, resource_factory: Callable[[], AsyncContextManager[ServiceResource]]
    ):
        self._resource_factory = resource_factory

    async def create_put_link(self, bucket: str, key: str, expiration=3600):
        async with self._resource_factory() as resource:
            client = resource.meta.client
            return await client.generate_presigned_url(
                "put_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expiration,
            )

    async def create_get_link(self, bucket, key, expiration=3600):
        async with self._resource_factory() as resource:
            client = resource.meta.client
            return await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expiration,
            )
