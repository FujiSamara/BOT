from app.schemas.file import ProxyInfoCreateSchema
from app.infra.database.models import ProxyInfo


def proxy_create_schema_to_proxy_info(proxy_create: ProxyInfoCreateSchema) -> ProxyInfo:
    return ProxyInfo(
        uuid=proxy_create.uuid,
        key=proxy_create.key,
        addr=proxy_create.addr,
        created=proxy_create.created.replace(tzinfo=None),
        running=proxy_create.running,
    )


def proxy_to_proxy_info_schema(proxy_info: ProxyInfo) -> ProxyInfoSchema:
    return ProxyInfoSchema.model_validate(proxy_info)
