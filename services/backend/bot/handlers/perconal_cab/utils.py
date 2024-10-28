from typing import Optional
from aiogram.types import InlineKeyboardButton
from aiogram.utils.markdown import hbold

from settings import get_settings
from bot.kb import get_personal_cabinet_button
from bot.text import personal_cabinet_logins_dict
from db.service import (
    get_worker_chief,
    get_material_value_by_inventory_number,
    get_worker_by_telegram_id,
    get_material_values,
    get_logins,
)
from db.schemas import WorkerSchema
from bot.handlers.perconal_cab.schemas import ShowLoginCallbackData


def menu_text(worker: WorkerSchema) -> str:
    department_chef: Optional[WorkerSchema] = get_worker_chief(
        telegram_id=worker.telegram_id
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

    return text


def get_material_values_text(callback_data: ShowLoginCallbackData) -> str:
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
    return text


def get_logins_bts(telegram_id: int) -> list[InlineKeyboardButton]:
    try:
        logins = [
            data
            for data in get_logins(get_worker_by_telegram_id(telegram_id).id)
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
    except Exception:
        buttons: list[InlineKeyboardButton] = []

    buttons.append([get_personal_cabinet_button])
    return buttons


def get_mat_vals_bts(telegram_id: int) -> list[InlineKeyboardButton]:
    material_values = get_material_values(telegram_id=telegram_id)
    buttons: list[InlineKeyboardButton] = []
    for material_value in material_values:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=material_value.item,
                    callback_data=ShowLoginCallbackData(
                        end_point="get_per_cab_mat_val",
                        inventory_number=material_value.inventory_number,
                    ).pack(),
                )
            ]
        )

    return buttons
