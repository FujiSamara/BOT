from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hbold
from aiogram.filters.callback_data import CallbackData
from typing import Optional
import asyncio
from bot.kb import (
    get_personal_cabinet,
    personal_cabinet_menu,
    personal_cabinet_menu_with_logins,
    get_per_cab_logins,
    get_per_cab_knowledge_base,
)
from bot.text import personal_cabinet_logins_dict
from bot.handlers.utils import try_edit_or_answer
from db.service import (
    get_worker_by_telegram_id,
    get_worker_chief,
    get_logins,
)
from db.schemas import WorkerSchema


class ShowLoginCallbackData(CallbackData, prefix="tech_req"):
    end_point: str
    login: str
    service: str


router = Router(name="personal_account")


@router.callback_query(F.data == get_personal_cabinet.callback_data)
async def get_personal_data(callback: CallbackQuery):
    worker: Optional[WorkerSchema] = get_worker_by_telegram_id(callback.message.chat.id)
    department_chef: Optional[WorkerSchema] = get_worker_chief(
        telegram_id=callback.message.chat.id
    )
    text = ""

    if worker.l_name is not None:
        text += hbold(worker.l_name) + " "
    if worker.f_name is not None:
        text += hbold(worker.f_name) + " "
    if worker.o_name is not None:
        text += hbold(worker.o_name) + " "

    text += f"\nДолжность: {worker.post.name}\n\
Предприятие: {worker.department.name}\n\
ФИО руководителя: "
    if department_chef is not None:
        if department_chef.l_name is not None:
            text += department_chef.l_name + " "
        if department_chef.f_name is not None:
            text += department_chef.f_name + " "
        if department_chef.o_name is not None:
            text += department_chef.o_name + " "
    else:
        text += "Не найден"
    text += f"\nДата приема на работу: {worker.employment_date}\n\
    "  # TODO Материальные ценности

    del worker
    del department_chef
    if get_logins(callback.message.chat.id):
        await try_edit_or_answer(
            text=text,
            reply_markup=personal_cabinet_menu_with_logins,
            message=callback.message,
        )
    else:
        await try_edit_or_answer(
            text=text,
            reply_markup=personal_cabinet_menu,
            message=callback.message,
        )


@router.callback_query(F.data == get_per_cab_logins.callback_data)
async def get_logins_pers_cab(callback: CallbackQuery):
    logins = [
        data
        for data in get_logins(get_worker_by_telegram_id(callback.message.chat.id).id)
        if data[0] not in ["id", "worker"]
    ]
    buttons: list[InlineKeyboardButton] = []
    for i in range(6):
        if logins[i][1]:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=personal_cabinet_logins_dict[logins[i][0]],
                        callback_data=ShowLoginCallbackData(
                            end_point="get_per_cab_login",
                            login=logins[i][1],
                            service=logins[i][0],
                        ).pack(),
                    )
                ]
            )
        print(logins[i][0], logins[i][1])
    buttons.append([get_personal_cabinet])
    await try_edit_or_answer(
        text=hbold("Логины"),
        message=callback.message,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(ShowLoginCallbackData.filter(F.end_point == "get_per_cab_login"))
async def show_login(callback: CallbackQuery, callback_data: ShowLoginCallbackData):
    await try_edit_or_answer(
        text=hbold(personal_cabinet_logins_dict[callback_data.service])
        + f"\n{callback_data.login}",
        message=callback.message,
    )
    await asyncio.sleep(delay=10)
    await get_logins_pers_cab(callback)


@router.callback_query(F.data == get_per_cab_knowledge_base.callback_data)
async def get_knowledge_base(callback: CallbackQuery):
    pass
