from pydantic_settings import BaseSettings
from pydantic import Field, computed_field


class PostgreSQLSettings(BaseSettings):
    psql_pass: str = Field(validation_alias="POSTGRES_PASSWORD")
    psql_user: str = Field(validation_alias="POSTGRES_USER")
    psql_host: str = Field(validation_alias="POSTGRES_HOST", default="127.0.0.1")
    psql_port: int = Field(validation_alias="POSTGRES_PORT", default=5432)
    psql_db_name: str = Field(validation_alias="POSTGRES_DB_NAME", default="postgres")

    @computed_field
    @property
    def psql_dsn(self) -> str:
        return (
            f"postgresql+psycopg://{self.psql_user}:{self.psql_pass}"
            + f"@{self.psql_host}:{self.psql_port}/{self.psql_db_name}"
        )
