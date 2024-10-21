import asyncio
from typing import Optional
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext

from bot.kb import (
    get_personal_cabinet,
    personal_cabinet_menu,
    personal_cabinet_menu_teller_cash,
    get_per_cab_logins,
    get_per_cab_mat_vals,
    set_per_cab_department,
    create_reply_keyboard,
)
from bot import text
from bot.states import PersconalCabinet, Base
from bot.handlers.utils import (
    try_edit_or_answer,
    try_delete_message,
)
from bot.handlers.perconal_cab import utils
from bot.handlers.perconal_cab.schemas import ShowLoginCallbackData
from db.service import (
    get_worker_by_telegram_id,
    get_departments_names,
    set_department_for_worker,
)
from db.schemas import WorkerSchema
from db.models import FujiScope


router = Router(name="personal_cabinet")


@router.callback_query(F.data == get_personal_cabinet.callback_data)
async def get_personal_data(callback: CallbackQuery):
    worker: Optional[WorkerSchema] = get_worker_by_telegram_id(callback.message.chat.id)

    if (
        FujiScope.bot_bid_teller_cash in worker.post.scopes
        or FujiScope.admin in worker.post.scopes
    ):
        reply_markup = personal_cabinet_menu_teller_cash
    else:
        reply_markup = personal_cabinet_menu

    text = utils.menu_text(worker)

    del worker

    await try_edit_or_answer(
        text=text,
        reply_markup=reply_markup,
        message=callback.message,
    )


async def get_personal_data_ms(message: Message):
    worker: Optional[WorkerSchema] = get_worker_by_telegram_id(message.chat.id)

    if (
        FujiScope.bot_bid_teller_cash in worker.post.scopes
        or FujiScope.admin in worker.post.scopes
    ):
        reply_markup = personal_cabinet_menu_teller_cash
    else:
        reply_markup = personal_cabinet_menu

    text = utils.menu_text(worker)

    del worker

    await try_edit_or_answer(
        text=text,
        reply_markup=reply_markup,
        message=message,
    )


@router.callback_query(F.data == get_per_cab_logins.callback_data)
async def get_logins_pers_cab(callback: CallbackQuery):
    await try_edit_or_answer(
        text=hbold("Доступы"),
        message=callback.message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=utils.get_logins(callback.message.chat.id)
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


@router.callback_query(F.data == get_per_cab_mat_vals.callback_data)
async def get_mat_vals(callback: CallbackQuery):
    await try_edit_or_answer(
        text=hbold(get_per_cab_mat_vals.text),
        message=callback.message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                utils.get_mat_vals_bts(callback.message.chat.id),
                [get_personal_cabinet],
            ]
        ),
    )


@router.callback_query(
    ShowLoginCallbackData.filter(F.end_point == "get_per_cab_mat_val")
)
async def get_mat_val(callback: CallbackQuery, callback_data: ShowLoginCallbackData):
    await try_edit_or_answer(
        text=utils.get_material_values_text,
        message=callback.message,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[get_per_cab_mat_vals]]),
    )


@router.callback_query(F.data == set_per_cab_department.callback_data)
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
async def change_department(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    departments_names = get_departments_names()
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await state.set_state(Base.none)
        await get_personal_data_ms(message=message)
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
                        inline_keyboard=[[get_personal_cabinet]]
                    ),
                )
            else:
                await message.answer(
                    text=hbold("Ошибка, не удалось изменить предприятие."),
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[[get_personal_cabinet]]
                    ),
                )
            await state.set_state(Base.none)
