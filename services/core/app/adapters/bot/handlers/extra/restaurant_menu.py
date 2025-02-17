import pathlib
from fastapi import UploadFile
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    Document,
    PhotoSize,
)
from aiogram.fsm.context import FSMContext
from app.adapters.bot.handlers.utils import (
    handle_documents_form,
    handle_documents,
    download_file,
)
from app.adapters.bot.states import Extra
from app.adapters.bot.kb import get_menu_changing_form_button
from app.adapters.bot.handlers.main_handler import send_menu_by_scopes
from app.infra.config import settings


router = Router()


@router.callback_query(F.data == get_menu_changing_form_button.callback_data)
async def get_menu_changing_form(callback: CallbackQuery, state: FSMContext):
    await handle_documents_form(callback.message, state, Extra.menu)


@router.message(Extra.menu)
async def set_documents(message: Message, state: FSMContext):
    def condition(documents: list[Document | PhotoSize]) -> str | None:
        if len(documents) > 1:
            return "Меню должно быть одно!"

    async def clear_state_with_success_caller(message: Message, state: FSMContext):
        data = await state.get_data()
        documents: list[Document | PhotoSize] = data["menu_document"]

        if len(documents) == 0:
            await state.clear()
            await send_menu_by_scopes(message)
            return

        document: UploadFile = await download_file(documents[0])

        path = pathlib.Path(settings.storage_path) / "menu.pdf"
        data = await document.read()

        with open(path, "wb") as f:
            f.write(data)

        await state.clear()
        await send_menu_by_scopes(message)

    await handle_documents(
        message, state, "menu_document", clear_state_with_success_caller, condition
    )
