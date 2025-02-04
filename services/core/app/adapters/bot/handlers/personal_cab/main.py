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

from app.infra.config import settings

from app.services import (
    get_worker_by_telegram_id,
    get_departments_names,
    set_department_for_worker,
    get_last_completed_worktimes_by_tg_id,
    get_work_time_record_by_id,
)
from app.schemas import WorkerSchema
from app.infra.database.models import FujiScope

from app.adapters.bot.kb import (
    get_personal_cabinet_button,
    get_per_cab_logins_button,
    get_per_cab_mat_vals_button,
    set_per_cab_department_button,
    get_per_cab_dismissal_button,
    get_menu_changing_form_button,
    get_per_cab_worktimes_button,
    main_menu_button,
    create_reply_keyboard,
)
from app.adapters.bot import text as text_imp
from app.adapters.bot.states import PersonalCabinet, Base
from app.adapters.bot.handlers.utils import (
    try_edit_or_answer,
    try_delete_message,
    handle_documents_form,
    handle_documents,
    download_file,
)
from app.adapters.bot.handlers.personal_cab import utils
from app.adapters.bot.handlers.personal_cab.schemas import (
    ShowLoginCallbackData,
    ShowWorkTimeCallbackData,
)


router = Router(name="personal_cabinet")


@router.callback_query(F.data == get_personal_cabinet_button.callback_data)
async def get_personal_data(message: CallbackQuery | Message):
    message = message.message if isinstance(message, CallbackQuery) else message

    worker: Optional[WorkerSchema] = get_worker_by_telegram_id(message.chat.id)

    buttons: list[list[InlineKeyboardButton]] = [
        [get_per_cab_logins_button],
        [get_per_cab_mat_vals_button],
        [get_per_cab_dismissal_button],
        [get_per_cab_worktimes_button],
    ]
    if (
        FujiScope.bot_bid_teller_cash in worker.post.scopes
        or FujiScope.admin in worker.post.scopes
    ):
        buttons.append([set_per_cab_department_button])

    if FujiScope.admin in worker.post.scopes:
        buttons.append([get_menu_changing_form_button])

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
        text=hbold(get_per_cab_logins_button.text),
        message=callback.message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=utils.get_logins_btns(callback.message.chat.id)
        ),
    )


@router.callback_query(ShowLoginCallbackData.filter(F.end_point == "get_per_cab_login"))
async def show_login(callback: CallbackQuery, callback_data: ShowLoginCallbackData):
    await try_edit_or_answer(
        text=hbold(text_imp.personal_cabinet_logins_dict[callback_data.service])
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
                *utils.get_mat_vals_btns(callback.message.chat.id),
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
    await state.set_state(PersonalCabinet.department)

    department_names = get_departments_names()
    department_names.sort()

    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите предприятие:"),
        reply_markup=create_reply_keyboard(text_imp.back, *department_names),
    )
    await state.update_data(msg=msg)


@router.message(PersonalCabinet.department)
async def set_department(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    departments_names = get_departments_names()
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text_imp.back:
        await state.set_state(Base.none)
        await get_personal_data(message)
    else:
        if message.text not in departments_names:
            departments_names.sort()
            msg = await message.answer(
                text=text_imp.format_err,
                reply_markup=create_reply_keyboard(text_imp.back, *departments_names),
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
@router.callback_query(F.data == get_menu_changing_form_button.callback_data)
async def get_menu_changing_form(callback: CallbackQuery, state: FSMContext):
    await handle_documents_form(callback.message, state, PersonalCabinet.menu)


@router.message(PersonalCabinet.menu)
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

        path = pathlib.Path(settings.storage_path) / "menu.pdf"
        data = await document.read()

        with open(path, "wb") as f:
            f.write(data)

        await state.clear()
        await get_personal_data(message)

    await handle_documents(
        message, state, "menu_document", clear_state_with_success_caller, condition
    )


# Worktimes


@router.callback_query(
    ShowWorkTimeCallbackData.filter(
        F.end_point == get_per_cab_worktimes_button.callback_data
    )
)
@router.callback_query(F.data == get_per_cab_worktimes_button.callback_data)
async def get_per_cab_worktimes(
    callback: CallbackQuery, callback_data: ShowWorkTimeCallbackData | None = None
):
    if callback_data is None:
        offset = 0
    else:
        offset = callback_data.page
    worktimes = get_last_completed_worktimes_by_tg_id(
        callback.message.chat.id, offset=offset
    )
    buttons: list[list[InlineKeyboardButton]] = []
    for worktime in worktimes:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{worktime.day.strftime(settings.date_format)} {'1<' if round(worktime.work_duration, 0) < 1 else round(worktime.work_duration, 0)}",
                    callback_data=ShowWorkTimeCallbackData(
                        end_point="per_cab_worktime",
                        id=worktime.id,
                    ).pack(),
                )
            ]
        )
    if offset != 0:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Прошлая страница",
                    callback_data=ShowWorkTimeCallbackData(
                        end_point=get_per_cab_worktimes_button.callback_data,
                        page=offset - 1,
                    ).pack(),
                )
            ]
        )
    else:
        if len(worktimes) == 10:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="Следующая страница",
                        callback_data=ShowWorkTimeCallbackData(
                            end_point=get_per_cab_worktimes_button.callback_data,
                            page=offset + 1,
                        ).pack(),
                    )
                ]
            )

    worker = get_worker_by_telegram_id(callback.message.chat.id)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(get_per_cab_worktimes_button.text)
        + f"\n{worker.l_name} {worker.f_name}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                *buttons,
                [get_personal_cabinet_button],
            ]
        ),
    )


@router.callback_query(
    ShowWorkTimeCallbackData.filter(F.end_point == "per_cab_worktime")
)
async def show_worktime(
    callback: CallbackQuery, callback_data: ShowWorkTimeCallbackData
):
    worktime = get_work_time_record_by_id(callback_data.id)
    text = f"{hbold('Смена от: ', worktime.day.strftime(settings.date_format))}\n"
    text += (
        f"{hbold('Сотрудник: ')} {worktime.worker.l_name} {worktime.worker.f_name}\n"
    )
    text += f"{hbold('Предприятие:')} {worktime.department.name if worktime.department is not None else 'Отсутствует'}\n"
    text += f"{hbold('Начало смены:')} {worktime.work_begin.strftime(settings.time_format) if worktime.work_begin is not None else 'Отсутствует'}\n"
    text += f"{hbold('Конец смены:')} {worktime.work_end.strftime(settings.time_format) if worktime.work_end is not None else 'Отсутствует'}\n"
    text += f"{hbold('Отработано часов:')} {'1<' if round(worktime.work_duration, 0) < 1 else round(worktime.work_duration, 0)}\n"
    text += f"{hbold('Оценка:')} {worktime.rating if worktime.rating is not None else 'Отсутствует'}\n"
    if worktime.fine is not None:
        text += f"{hbold('Штраф:')} {worktime.fine} р."
    await try_edit_or_answer(
        message=callback.message,
        text=text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=text_imp.back,
                        callback_data=get_per_cab_worktimes_button.callback_data,
                    )
                ]
            ]
        ),
    )
