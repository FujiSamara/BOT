from common.config import (
    NetworkSettings,
    LocalAuthSettings,
    RemoteAuthSettings,
    FileSettings,
)
from app.infra.config.database import DBSettings


class Settings(
    NetworkSettings, LocalAuthSettings, RemoteAuthSettings, FileSettings, DBSettings
):
    pass
