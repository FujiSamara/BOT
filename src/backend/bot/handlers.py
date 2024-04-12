from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

router = Router(name="main")

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")