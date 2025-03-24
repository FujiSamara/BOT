from common.config import (
    NetworkSettings,
    LocalAuthSettings,
    RemoteAuthSettings,
    FileSettings,
    AdminSettings,
)
from app.infra.config.database import DBSettings


class Settings(
    NetworkSettings,
    LocalAuthSettings,
    RemoteAuthSettings,
    FileSettings,
    DBSettings,
    AdminSettings,
):
    pass
