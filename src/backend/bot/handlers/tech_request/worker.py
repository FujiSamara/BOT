from aiogram import Router, F

from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from fastapi import UploadFile

from bot import text, kb
from bot.states import (
    Base,
    WorkerTechnicalRequestForm,
)
from bot.handlers.utils import (
    notify_worker_by_telegram_id,
    try_edit_or_answer,
    try_delete_message,
    download_file,
    handle_documents_form,
    handle_documents,
)
from bot.handlers.tech_request.utils import show_form
from bot.handlers.tech_request.schemas import ShowRequestCallbackData
from bot.handlers.tech_request import kb as tech_kb

from db.service import (
    get_all_history_technical_requests_for_worker,
    get_all_waiting_technical_requests_for_worker,
    get_technical_problem_names,
    create_technical_request,
)


router = Router(name="technical_request_worker")


@router.callback_query(F.data == tech_kb.WR_menu_button.callback_data)
async def show_worker_menu(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.WR_menu,
    )


@router.callback_query(F.data == tech_kb.WR_create.callback_data)
async def show_worker_create_request_format_cb(
    callback: CallbackQuery, state: FSMContext
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Создать заявку"),
        reply_markup=await tech_kb.WR_create_kb(state),
    )


async def show_worker_create_request_format_ms(
    message: CallbackQuery, state: FSMContext
):
    await try_edit_or_answer(
        message=message,
        text=hbold("Создать заявку"),
        reply_markup=await tech_kb.WR_create_kb(state),
    )


@router.callback_query(F.data == "problem_type_WR_TR")
async def get_problem(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerTechnicalRequestForm.problem_name)
    problems = get_technical_problem_names()
    problems.sort()
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите проблему:"),
        reply_markup=kb.create_reply_keyboard(
            text.back, *[problem for problem in problems]
        ),
    )
    await state.update_data(msg=msg)


@router.message(WorkerTechnicalRequestForm.problem_name)
async def set_problem(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await state.set_state(Base.none)
        await show_worker_create_request_format_ms(message, state)
    else:
        problems = get_technical_problem_names()
        if message.text not in problems:
            problems.sort()
            msg = await message.answer(
                text=text.format_err,
                reply_markup=kb.create_reply_keyboard(
                    *[problem for problem in problems]
                ),
            )
            await state.update_data(msg=msg)
            return
        await state.update_data(problem_name=message.text)
        await show_worker_create_request_format_ms(message, state)
        await state.set_state(Base.none)


@router.callback_query(F.data == "description_WR_TR")
async def get_description(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerTechnicalRequestForm.description)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(text=hbold("Введите описание проблемы:"))
    await state.update_data(msg=msg)


@router.message(WorkerTechnicalRequestForm.description)
async def set_description(message: Message, state: FSMContext):
    await state.set_state(Base.none)
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await state.update_data(description=message.text)
    await try_delete_message(message)
    await show_worker_create_request_format_ms(message, state)


@router.callback_query(F.data == "photo_WR_TR")
async def get_worker_photo(callback: CallbackQuery, state: FSMContext):
    await handle_documents_form(
        callback.message, state, WorkerTechnicalRequestForm.photo
    )


@router.message(WorkerTechnicalRequestForm.photo)
async def set_worker_photo(message: Message, state: FSMContext):
    await handle_documents(
        message, state, "photo", show_worker_create_request_format_ms
    )


@router.callback_query(F.data == tech_kb.WR_waiting.callback_data)
async def show_worker_waiting_menu(callback: CallbackQuery):
    requests = get_all_waiting_technical_requests_for_worker(
        telegram_id=callback.message.chat.id
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Ожидающие заявки"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="WR_TR_show_form_waiting",
            menu_button=tech_kb.WR_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "WR_TR_show_form_waiting")
)
async def show_worker_waiting_form(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = []
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.WR_waiting,
    )


@router.callback_query(F.data == tech_kb.WR_history.callback_data)
async def show_worker_history_menu(callback: CallbackQuery):
    requests = get_all_history_technical_requests_for_worker(
        telegram_id=callback.message.chat.id
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("История заявок"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="WR_TR_show_form_history",
            menu_button=tech_kb.WR_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "WR_TR_show_form_history")
)
async def show_worker_history_form(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = []
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.WR_history,
    )


@router.callback_query(F.data == "send_WR_TR")
async def save_worker_request(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    problem_name = data["problem_name"]
    description = data["description"]

    photo = data["photo"]
    photo_files: list[UploadFile] = []
    for doc in photo:
        photo_files.append(await download_file(doc))

    ret_data = create_technical_request(
        problem_name=problem_name,
        description=description,
        photo_files=photo_files,
        telegram_id=callback.message.chat.id,
    )

    await notify_worker_by_telegram_id(
        id=ret_data["repairman_telegram_id"],
        message=text.notification_repairman
        + f"\nНа производстве: {ret_data["department_name"]}",
    )

    await state.clear()
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.WR_menu,
    )
