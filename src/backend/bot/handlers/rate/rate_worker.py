from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from db import service
from settings import get_settings
from bot.handlers.utils import try_edit_or_answer
from bot.handlers.rate.utils import get_shift_status
from bot.kb import (
    create_inline_keyboard,
    main_menu_button,
    rating_menu_button,
    get_rating_worker_menu,
)
from bot.text import err
from bot.handlers.rate.schemas import RateShiftCallbackData, RateFormStatus
from bot.states import RateForm

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
                callback_data=RateShiftCallbackData(day=day, record_id=-1).pack(),
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
            buttons.append(
                InlineKeyboardButton(
                    text=f"{worker_info} {time} {label}",
                    callback_data=RateShiftCallbackData(
                        day=date, record_id=record.id
                    ).pack(),
                )
            )
        else:
            buttons.append(
                InlineKeyboardButton(
                    text=f"Работник не найден {time} {label}",
                    callback_data=RateShiftCallbackData(
                        day=date, record_id=record.id
                    ).pack(),
                )
            )

    buttons.append(rating_menu_button)

    keyboard = create_inline_keyboard(*buttons)

    await try_edit_or_answer(
        message=callback.message, text="Выберите работника:", reply_markup=keyboard
    )


@router.callback_query(RateShiftCallbackData.filter(F.record_id != -1))
async def get_worker_menu(
    callback: CallbackQuery, callback_data: RateShiftCallbackData
):
    # Settings data
    record = service.get_work_time_record_by_id(callback_data.record_id)
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

    # Settings buttons and keyboard
    keyboard = get_rating_worker_menu(fine, rating)

    await try_edit_or_answer(
        message=callback.message,
        text=f"{worker_info} {time_begin}\nНа смене был: {record.work_duration} часов.",
        reply_markup=keyboard,
    )


@router.callback_query(
    RateShiftCallbackData.filter(F.form_status != RateFormStatus.NONE)
)
async def get_input_form(
    callback: CallbackQuery, state: FSMContext, callback_data: RateShiftCallbackData
):
    text = "Введите значение:"
    await state.update_data(record_id=callback_data.record_id)
    if callback_data.form_status == RateFormStatus.FINE:
        await state.set_state(RateForm.fine)
        text = "Введите штраф:"
    elif callback_data.form_status == RateFormStatus.RATING:
        await state.set_state(RateForm.rating)
        text = "Введите оценку:"

    await try_edit_or_answer(message=callback.message, text=text)


@router.message(RateForm.rating)
async def set_rating(message: Message, state: FSMContext):
    try:
        rating = int(message.text)
    except Exception:
        await try_edit_or_answer(
            message,
        )

    # if fine != 0 or rating != 0:
    #     record.rating = rating
    #     record.fine = fine

    #     service.update_work_time_record(record)
