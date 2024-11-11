import asyncio
import pathlib
from typing import Optional
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Document,
    PhotoSize,
)
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from fastapi import UploadFile

from settings import get_settings

from db.service import (
    get_worker_by_telegram_id,
    get_departments_names,
    set_department_for_worker,
)
from db.schemas import WorkerSchema
from db.models import FujiScope

from bot.kb import (
    get_personal_cabinet_button,
    get_per_cab_logins_button,
    get_per_cab_mat_vals_button,
    set_per_cab_department_button,
    get_per_cab_dismissal_button,
    get_menu_changing_form_buttom,
    main_menu_button,
    create_reply_keyboard,
)
from bot import text
from bot.states import PersconalCabinet, Base
from bot.handlers.utils import (
    try_edit_or_answer,
    try_delete_message,
    handle_documents_form,
    handle_documents,
    download_file,
)
from bot.handlers.perconal_cab import utils
from bot.handlers.perconal_cab.schemas import ShowLoginCallbackData


router = Router(name="personal_cabinet")


@router.callback_query(F.data == get_personal_cabinet_button.callback_data)
async def get_personal_data(message: CallbackQuery | Message):
    message = message.message if isinstance(message, CallbackQuery) else message

    worker: Optional[WorkerSchema] = get_worker_by_telegram_id(message.chat.id)

    buttons: list[list[InlineKeyboardButton]] = [
        [get_per_cab_logins_button],
        [get_per_cab_mat_vals_button],
        [get_per_cab_dismissal_button],
    ]
    if (
        FujiScope.bot_bid_teller_cash in worker.post.scopes
        or FujiScope.admin in worker.post.scopes
    ):
        buttons.append([set_per_cab_department_button])

    if FujiScope.admin in worker.post.scopes:
        buttons.append([get_menu_changing_form_buttom])

    buttons.append([main_menu_button])

    text = utils.menu_text(worker)

    await try_edit_or_answer(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        message=message,
    )


@router.callback_query(F.data == get_per_cab_logins_button.callback_data)
async def get_logins_pers_cab(callback: CallbackQuery):
    await try_edit_or_answer(
        text=hbold("Доступы"),
        message=callback.message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=utils.get_logins_bts(callback.message.chat.id)
        ),
    )


@router.callback_query(ShowLoginCallbackData.filter(F.end_point == "get_per_cab_login"))
async def show_login(callback: CallbackQuery, callback_data: ShowLoginCallbackData):
    await try_edit_or_answer(
        text=hbold(text.personal_cabinet_logins_dict[callback_data.service])
        + f"\n{callback_data.login}",
        message=callback.message,
    )
    await asyncio.sleep(delay=10)
    await get_logins_pers_cab(callback)


@router.callback_query(F.data == get_per_cab_mat_vals_button.callback_data)
async def get_mat_vals(callback: CallbackQuery):
    await try_edit_or_answer(
        text=hbold(get_per_cab_mat_vals_button.text),
        message=callback.message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                *utils.get_mat_vals_bts(callback.message.chat.id),
                [get_personal_cabinet_button],
            ]
        ),
    )


@router.callback_query(
    ShowLoginCallbackData.filter(F.end_point == "get_per_cab_mat_val")
)
async def get_mat_val(callback: CallbackQuery, callback_data: ShowLoginCallbackData):
    await try_edit_or_answer(
        text=utils.get_material_values_text(callback_data=callback_data),
        message=callback.message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[get_per_cab_mat_vals_button]]
        ),
    )


@router.callback_query(F.data == set_per_cab_department_button.callback_data)
async def get_department(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PersconalCabinet.department)

    department_names = get_departments_names()
    department_names.sort()

    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите предприятие:"),
        reply_markup=create_reply_keyboard(text.back, *department_names),
    )
    await state.update_data(msg=msg)


@router.message(PersconalCabinet.department)
async def set_department(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    departments_names = get_departments_names()
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await state.set_state(Base.none)
        await get_personal_data(message)
    else:
        if message.text not in departments_names:
            departments_names.sort()
            msg = await message.answer(
                text=text.format_err,
                reply_markup=create_reply_keyboard(text.back, *departments_names),
            )
            await state.update_data(msg=msg)

        else:
            if set_department_for_worker(
                telegram_id=message.chat.id, department_name=message.text
            ):
                await message.answer(
                    text=hbold(f"Предприятие изменено на {message.text}"),
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[[get_personal_cabinet_button]]
                    ),
                )
            else:
                await message.answer(
                    text=hbold("Ошибка, не удалось изменить предприятие."),
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[[get_personal_cabinet_button]]
                    ),
                )
            await state.set_state(Base.none)


# Documents
@router.callback_query(F.data == get_menu_changing_form_buttom.callback_data)
async def get_menu_changing_form(callback: CallbackQuery, state: FSMContext):
    await handle_documents_form(callback.message, state, PersconalCabinet.menu)


@router.message(PersconalCabinet.menu)
async def set_documents(message: Message, state: FSMContext):
    def condition(documents: list[Document | PhotoSize]) -> str | None:
        if len(documents) > 1:
            return "Меню должно быть одно!"

    async def clear_state_with_success_caller(message: Message, state: FSMContext):
        data = await state.get_data()
        documents: list[Document | PhotoSize] = data["menu_document"]

        if len(documents) == 0:
            await state.clear()
            await get_personal_data(message)
            return

        document: UploadFile = await download_file(documents[0])

        path = pathlib.Path(get_settings().storage_path) / "menu.pdf"
        data = await document.read()

        with open(path, "wb") as f:
            f.write(data)

        await state.clear()
        await get_personal_data(message)

    await handle_documents(
        message, state, "menu_document", clear_state_with_success_caller, condition
    )
