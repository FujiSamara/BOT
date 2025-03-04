from common.config import (
    PostgreSQLSettings,
    NetworkSettings,
    LocalAuthSettings,
    AdminSettings,
)


class Settings(
    PostgreSQLSettings,
    NetworkSettings,
    LocalAuthSettings,
    AdminSettings,
):
    pass
