from common.config import (
    PostgreSQLSettings,
    NetworkSettings,
    LocalAuthSettings,
)


class Settings(PostgreSQLSettings, NetworkSettings, LocalAuthSettings):
    pass
