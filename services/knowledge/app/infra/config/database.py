from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class DBSettings(BaseSettings):
    knowledge_psql_pass: str = Field(validation_alias="KNOWLEDGE_POSTGRES_PASSWORD")
    knowledge_psql_user: str = Field(validation_alias="KNOWLEDGE_POSTGRES_USER")
    knowledge_psql_schema: str = Field(validation_alias="KNOWLEDGE_POSTGRES_SCHEMA")
    knowledge_psql_host: str = Field(
        validation_alias="KNOWLEDGE_POSTGRES_HOST", default="127.0.0.1"
    )
    knowledge_psql_port: int = Field(
        validation_alias="KNOWLEDGE_POSTGRES_PORT", default=5432
    )
    knowledge_psql_db_name: str = Field(
        validation_alias="KNOWLEDGE_POSTGRES_DB_NAME", default="postgres"
    )

    @computed_field
    @property
    def knowledge_ppsql_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.knowledge_psql_user}:{self.knowledge_psql_pass}"
            + f"@{self.knowledge_psql_host}:{self.knowledge_psql_port}/{self.knowledge_psql_db_name}"
        )

    dish_psql_pass: str = Field(validation_alias="DISH_POSTGRES_PASSWORD")
    dish_psql_user: str = Field(validation_alias="DISH_POSTGRES_USER")
    dish_psql_schema: str = Field(validation_alias="DISH_POSTGRES_SCHEMA")
    dish_psql_host: str = Field(
        validation_alias="DISH_POSTGRES_HOST", default="127.0.0.1"
    )
    dish_psql_port: int = Field(validation_alias="DISH_POSTGRES_PORT", default=5432)
    dish_psql_db_name: str = Field(
        validation_alias="DISH_POSTGRES_DB_NAME", default="postgres"
    )

    @computed_field
    @property
    def dish_psql_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.dish_psql_user}:{self.dish_psql_pass}"
            + f"@{self.dish_psql_host}:{self.dish_psql_port}/{self.dish_psql_db_name}"
        )
