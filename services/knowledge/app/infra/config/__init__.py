from common.config import (
    PostgreSQLSettings,
    NetworkSettings,
    LocalAuthSettings,
    RemoteAuthSettings,
)


class Settings(
    PostgreSQLSettings, NetworkSettings, LocalAuthSettings, RemoteAuthSettings
):
    pass
