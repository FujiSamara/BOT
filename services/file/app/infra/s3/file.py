from typing import AsyncContextManager, Callable, Iterator
from itertools import islice

from mypy_boto3_s3 import ServiceResource
from mypy_boto3_s3.type_defs import DeleteObjectsOutputTypeDef, ErrorTypeDef


from app.contracts.clients import FileClient, KeyErrorSchema


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

    async def _delete_chunk(
        self, bucket: str, keys: list[str]
    ) -> DeleteObjectsOutputTypeDef:
        async with self._resource_factory() as resource:
            client = resource.meta.client
            delete_body = {"Objects": [{"Key": key} for key in keys], "Quiet": False}

            return await client.delete_objects(Bucket=bucket, Delete=delete_body)

    async def _delete_keys(
        self, bucket: str, keys: list[str], *, chunk_size: int
    ) -> list[ErrorTypeDef]:
        chunk_it = iter(keys)
        chunks: Iterator[list[int]] = iter(
            lambda: list(islice(chunk_it, chunk_size)), []
        )

        errors: list[ErrorTypeDef] = []

        for chunk in chunks:
            resp = await self._delete_chunk(bucket, chunk)

            errors.extend(resp.get("Errors", []))

        return errors

    async def delete(self, keys_buckets):
        bucket_keys_dict: dict[str, list[str]] = {}

        for key, bucket in keys_buckets:
            bucket_keys_dict.setdefault(bucket, []).append(key)

        errors: list[KeyErrorSchema] = []

        for bucket, keys in bucket_keys_dict.items():
            resp = await self._delete_keys(bucket, keys, chunk_size=1000)
            errors.extend(
                (
                    KeyErrorSchema(key=error["Key"], message=error["Message"])
                    for error in resp
                )
            )

        return errors
