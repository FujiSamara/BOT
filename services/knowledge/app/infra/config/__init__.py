from common.config import (
    PostgreSQLSettings,
    NetworkSettings,
    LocalAuthSettings,
    RemoteAuthSettings,
    FileSettings,
)


class Settings(
    PostgreSQLSettings,
    NetworkSettings,
    LocalAuthSettings,
    RemoteAuthSettings,
    FileSettings,
):
    pass
