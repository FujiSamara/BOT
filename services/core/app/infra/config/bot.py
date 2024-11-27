from pydantic import Field
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    bot_token: str = Field(validate_default="BOT_TOKEN")
    telegram_token: str = Field(validate_default="TELEGRAM_TOKEN")
    bot_webhook_url: str = Field(validate_default="BOT_WEBHOOK_URL")
