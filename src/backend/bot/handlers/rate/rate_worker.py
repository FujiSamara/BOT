from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from datetime import datetime, timedelta

from db import service
from settings import get_settings
from bot.handlers.utils import try_edit_or_answer
from bot.handlers.rate.utils import get_shift_status
from bot.kb import create_inline_keyboard, main_menu_button, rating_menu_button
from bot.handlers.rate.schemas import RateShiftCallbackData

router = Router(name="rating")


@router.callback_query(F.data == rating_menu_button.callback_data)
async def get_rating_list(callback: CallbackQuery):
    department = service.get_worker_department_by_telegram_id(callback.message.chat.id)
    day = datetime.now().date()

    day -= timedelta(days=8)

    buttons = []

    for i in range(10):
        label = ""

        if get_shift_status(day, department.id):
            label = "✅"
        elif i != 0:
            label = "❗️"

        buttons.append(
            InlineKeyboardButton(
                text=day.strftime(get_settings().date_format) + f" {label}",
                callback_data=RateShiftCallbackData(day=day, worker_id=-1).pack(),
            )
        )

        day -= timedelta(days=1)

    buttons.append(main_menu_button)

    keyboard = create_inline_keyboard(*buttons)

    await try_edit_or_answer(
        message=callback.message, text="Выберите смену:", reply_markup=keyboard
    )


@router.callback_query(RateShiftCallbackData.filter(F.worker_id == -1))
async def get_shift(callback: CallbackQuery, callback_data: RateShiftCallbackData):
    department = service.get_worker_department_by_telegram_id(callback.message.chat.id)
    date = callback_data.day
    records = service.get_work_time_records_by_day_and_department(department.id, date)

    buttons = []

    for record in records:
        time = record.work_begin.split()[1]
        label = ""

        if record.fine or record.rating:
            label = "✅"

        if record.worker:
            worker_info = (
                f"{record.worker.l_name} "
                + f"{record.worker.f_name} "
                + f"{record.worker.o_name}"
            )
            worker_id = record.worker.id
            buttons.append(
                InlineKeyboardButton(
                    text=f"{worker_info} {time}{label}",
                    callback_data=RateShiftCallbackData(
                        day=date, worker_id=worker_id
                    ).pack(),
                )
            )
        else:
            buttons.append(
                InlineKeyboardButton(
                    text=f"Работник не найден {time}{label}",
                    callback_data=rating_menu_button.callback_data,
                )
            )

    buttons.append(rating_menu_button)

    keyboard = create_inline_keyboard(*buttons)

    await try_edit_or_answer(
        message=callback.message, text="Выберите работника:", reply_markup=keyboard
    )


@router.callback_query(RateShiftCallbackData.filter(F.worker_id != -1))
async def get_worker_menu(
    callback: CallbackQuery, callback_data: RateShiftCallbackData
):
    # Settings data
    worker = service.get_worker_by_id(callback_data.worker_id)
    date = callback_data.day
    record = service.get_work_time_record_by_day_and_worker(
        callback_data.worker_id, date
    )
    time_begin = record.work_begin.split()[1]
    fine = record.fine
    rating = record.rating

    worker_info = "Работник не найден"

    if record.worker:
        worker_info = (
            f"{record.worker.l_name} "
            + f"{record.worker.f_name} "
            + f"{record.worker.o_name}"
        )

        worker_id = record.worker.id

    # Settings buttons and keyboard
    buttons = []

    keyboard = create_inline_keyboard(*buttons)

    buttons.append(
        InlineKeyboardButton(
            text=f"{worker_info} {time_begin}\n",
            callback_data=RateShiftCallbackData(day=date, worker_id=worker_id).pack(),
        )
    )

    await try_edit_or_answer(
        message=callback.message,
        text=f"{worker_info} {time_begin}" + f"На смене: {record.work_duration} часов.",
        reply_markup=keyboard,
    )
