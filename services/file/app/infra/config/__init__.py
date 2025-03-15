from common.config import (
    PostgreSQLSettings,
    NetworkSettings,
    LocalAuthSettings,
    AdminSettings,
)
from app.infra.config.s3 import S3Settings


class Settings(
    PostgreSQLSettings, NetworkSettings, LocalAuthSettings, AdminSettings, S3Settings
):
    pass
