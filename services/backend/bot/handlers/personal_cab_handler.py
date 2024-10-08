import asyncio
from typing import Optional
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.markdown import hbold
from settings import get_settings
from bot.kb import (
    get_personal_cabinet,
    personal_cabinet_menu,
    get_per_cab_logins,
    get_per_cab_mat_vals,
)
from bot.text import personal_cabinet_logins_dict
from bot.handlers.utils import try_edit_or_answer
from db.service import (
    get_worker_by_telegram_id,
    get_worker_chief,
    get_logins,
    get_material_values,
    get_material_value_by_inventory_number,
)
from db.schemas import WorkerSchema


class ShowLoginCallbackData(CallbackData, prefix="tech_req"):
    end_point: str
    login: Optional[str] = None
    service: Optional[str] = None
    inventory_number: Optional[str] = None


router = Router(name="personal_account")


@router.callback_query(F.data == get_personal_cabinet.callback_data)
async def get_personal_data(callback: CallbackQuery):
    worker: Optional[WorkerSchema] = get_worker_by_telegram_id(callback.message.chat.id)
    department_chef: Optional[WorkerSchema] = get_worker_chief(
        telegram_id=callback.message.chat.id
    )
    text = (
        hbold(worker.l_name) + " " + hbold(worker.f_name) + " " + hbold(worker.o_name)
    )

    text += f"\nДолжность: {worker.post.name}\n\
Предприятие: {worker.department.name}\n\
ФИО руководителя: "
    if department_chef is not None:
        text += (
            department_chef.l_name
            + " "
            + department_chef.f_name
            + " "
            + department_chef.o_name
        )
    else:
        text += "Не найден"
    text += f"\nДата приема на работу: {worker.employment_date}\n"

    del worker
    del department_chef
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
    for i in range(len(logins)):
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
    buttons.append([get_personal_cabinet])
    await try_edit_or_answer(
        text=hbold("Доступы"),
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


@router.callback_query(F.data == get_per_cab_mat_vals.callback_data)
async def get_mat_vals(callback: CallbackQuery):
    material_values = get_material_values(telegram_id=callback.message.chat.id)
    buttons: list[InlineKeyboardButton] = []
    for material_value in material_values:
        buttons.append(
            InlineKeyboardButton(
                text=material_value.item,
                callback_data=ShowLoginCallbackData(
                    end_point="get_per_cab_mat_val",
                    inventory_number=material_value.inventory_number,
                ).pack(),
            )
        )
    del material_values

    await try_edit_or_answer(
        text=hbold(get_per_cab_mat_vals.text),
        message=callback.message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[buttons, [get_personal_cabinet]]
        ),
    )


@router.callback_query(
    ShowLoginCallbackData.filter(F.end_point == "get_per_cab_mat_val")
)
async def get_mat_val(callback: CallbackQuery, callback_data: ShowLoginCallbackData):
    material_value = get_material_value_by_inventory_number(
        inventory_number=callback_data.inventory_number
    )

    text = f"Предмет: {material_value.item}\
\nКоличество: {material_value.quanity}\
\nСтоимость: {material_value.price}\
\nДата выдачи: {material_value.issue_date.date().strftime(get_settings().date_format)}"
    if material_value.return_date:
        text += f"\nДата возврата: {material_value.return_date.date().strftime(get_settings().date_format)}"
    text += f"\nИнвентаризационный номер: {material_value.inventory_number}"
    await try_edit_or_answer(
        text=text,
        message=callback.message,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[get_per_cab_mat_vals]]),
    )
