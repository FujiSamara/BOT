from app.infra.logging.logger import logger
from asyncio import sleep
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from fastapi import UploadFile

from app.adapters.bot import text, kb
from app.adapters.bot.states import (
    Base,
    WorkerDepartmentRequestForm,
)
from app.adapters.bot.handlers.utils import (
    try_edit_or_answer,
    try_delete_message,
    download_file,
    handle_documents_form,
    handle_documents,
    create_reply_keyboard,
)
from app.adapters.bot.handlers.department_request.utils import (
    show_form_technician,
    show_form_cleaning,
)
from app.adapters.bot.handlers.department_request.schemas import (
    ShowRequestCallbackData,
    PageCallbackData,
    RequestType,
)
from app.adapters.bot.handlers.department_request import kb as department_kb

from app.services import (
    get_all_history_technical_requests_for_worker,
    get_all_history_cleaning_requests_for_worker,
    get_all_waiting_technical_requests_for_worker,
    get_all_waiting_cleaning_requests_for_worker,
    get_technical_problem_names,
    get_cleaning_problem_names,
    create_technical_request,
    create_cleaning_request,
    get_departments_names,
)


router = Router(name="technical_request_worker")


@router.callback_query(F.data == department_kb.wr_menu_button.callback_data)
async def show_worker_menu(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(department_kb.wr_menu_button.text),
        reply_markup=department_kb.wr_menu,
    )


@router.callback_query(F.data == department_kb.wr_create.callback_data)
async def show_worker_create_request_format(
    message: Message | CallbackQuery, state: FSMContext
):
    if isinstance(message, CallbackQuery):
        message = message.message

    await try_edit_or_answer(
        message=message,
        text=hbold("Создать заявку"),
        reply_markup=await department_kb.wr_create_kb(state),
    )


@router.callback_query(F.data == "problem_group_WR_TR_CR")
async def get_problem_group(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerDepartmentRequestForm.problem_group)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите направленность проблемы:"),
        reply_markup=kb.create_reply_keyboard(text.back, *text.problem_groups),
    )
    await state.update_data(msg=msg)


@router.message(WorkerDepartmentRequestForm.problem_group)
async def set_problem_group(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await state.set_state(Base.none)
        await show_worker_create_request_format(message, state)
    else:
        if message.text not in text.problem_groups:
            msg = await message.answer(
                text=text.format_err,
                reply_markup=kb.create_reply_keyboard(text.back, *text.problem_groups),
            )
            await state.update_data(msg=msg)
            return

        await state.update_data(problem_group=text.problem_groups_dict[message.text])
        await state.set_state(Base.none)
        await get_problem(message, state)


async def get_problem(message: Message, state: FSMContext):
    await state.set_state(WorkerDepartmentRequestForm.problem_name)
    data = await state.get_data()
    problems = (
        get_technical_problem_names()
        if data["problem_group"] == "TR"
        else get_cleaning_problem_names()
    )
    problems.sort()
    await try_delete_message(message)
    msg = await message.answer(
        text=hbold("Выберите проблему:"),
        reply_markup=kb.create_reply_keyboard(
            text.back, *[problem for problem in problems]
        ),
    )
    await state.update_data(msg=msg)


@router.message(WorkerDepartmentRequestForm.problem_name)
async def set_problem(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await state.set_state(Base.none)
        await show_worker_create_request_format(message, state)
    else:
        problems = (
            get_technical_problem_names()
            if data["problem_group"] == "TR"
            else get_cleaning_problem_names()
        )
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
        await show_worker_create_request_format(message, state)
        await state.set_state(Base.none)


@router.callback_query(F.data == "description_WR_TR_CR")
async def get_description(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerDepartmentRequestForm.description)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(text=hbold("Введите описание проблемы:"))
    await state.update_data(msg=msg)


@router.message(WorkerDepartmentRequestForm.description)
async def set_description(message: Message, state: FSMContext):
    await state.set_state(Base.none)
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await state.update_data(description=message.text)
    await try_delete_message(message)
    await show_worker_create_request_format(message, state)


@router.callback_query(F.data == "photo_WR_TR_CR")
async def get_worker_photo(callback: CallbackQuery, state: FSMContext):
    await handle_documents_form(
        callback.message, state, WorkerDepartmentRequestForm.photo
    )


@router.message(WorkerDepartmentRequestForm.photo)
async def set_worker_photo(message: Message, state: FSMContext):
    await handle_documents(message, state, "photo", show_worker_create_request_format)


@router.callback_query(F.data == "department_WR_TR_CR")
async def get_department(message: Message | CallbackQuery, state: FSMContext):
    if isinstance(message, CallbackQuery):
        await try_delete_message(message=message.message)
        message = message.message
    await state.set_state(WorkerDepartmentRequestForm.department)
    await state.update_data(
        msg=await try_edit_or_answer(
            message=message,
            text=hbold("Выберите предприятие:"),
            reply_markup=create_reply_keyboard(text.back, *get_departments_names()),
            return_message=True,
        )
    )


@router.message(WorkerDepartmentRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    await try_delete_message((await state.get_data()).get("msg"))
    dep_name = message.text
    await try_delete_message(message=message)
    await state.set_state(Base.none)
    if dep_name == text.back:
        await show_worker_create_request_format(message, state)
    elif dep_name in get_departments_names():
        await state.update_data(dep_name=dep_name)
        await show_worker_create_request_format(message, state)
    else:
        msg = await try_edit_or_answer(
            message=message,
            text=text.format_err,
            return_message=True,
        )
        await sleep(3)
        await try_delete_message(msg)
        await get_department(message, state)


@router.callback_query(F.data == department_kb.wr_waiting.callback_data)
async def change_waiting_type(callback: CallbackQuery):
    buttons = [
        InlineKeyboardButton(
            text="Технические заявки",
            callback_data=PageCallbackData(
                page=0,
                requests_endpoint="WR_DR_waiting_menu",
                req_type=RequestType.TR.value,
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Заявки в клининг",
            callback_data=PageCallbackData(
                page=0,
                requests_endpoint="WR_DR_waiting_menu",
                req_type=RequestType.CR.value,
            ).pack(),
        ),
        InlineKeyboardButton(
            text=text.back,
            callback_data=department_kb.wr_menu_button.callback_data,
        ),
    ]
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тип заявок") + "\nОжидающие ",
        reply_markup=kb.create_inline_keyboard(*buttons),
    )


@router.callback_query(
    PageCallbackData.filter(F.requests_endpoint == "WR_DR_waiting_menu")
)
async def show_worker_waiting_menu(
    callback: CallbackQuery,
    callback_data: PageCallbackData,
):
    reply_markup = (
        department_kb.create_kb_with_end_point_TR(
            end_point="WR_DR_show_form_waiting",
            menu_button=department_kb.wr_waiting,
            requests=get_all_waiting_technical_requests_for_worker(
                telegram_id=callback.message.chat.id,
                page=callback_data.page,
            ),
            page=callback_data.page,
            requests_endpoint=callback_data.requests_endpoint,
        )
        if callback_data.req_type == RequestType.TR.value
        else department_kb.create_kb_with_end_point_CR(
            end_point="WR_DR_show_form_waiting",
            menu_button=department_kb.wr_waiting,
            requests=get_all_waiting_cleaning_requests_for_worker(
                tg_id=callback.message.chat.id,
                page=callback_data.page,
            ),
            page=callback_data.page,
            requests_endpoint=callback_data.requests_endpoint,
        )
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Ожидающие заявки"),
        reply_markup=reply_markup,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "WR_DR_show_form_waiting")
)
async def show_worker_waiting_form(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = []
    if callback_data.req_type == RequestType.TR.value:
        await show_form_technician(
            callback=callback,
            callback_data=callback_data,
            state=state,
            buttons=buttons,
            history_or_waiting_button=department_kb.wr_waiting,
        )
    else:
        await show_form_cleaning(
            callback=callback,
            callback_data=callback_data,
            state=state,
            buttons=buttons,
            history_or_waiting_button=department_kb.wr_waiting,
        )


@router.callback_query(F.data == department_kb.wr_history.callback_data)
async def change_history_type(callback: CallbackQuery):
    buttons = [
        InlineKeyboardButton(
            text="Технические заявки",
            callback_data=PageCallbackData(
                page=0,
                requests_endpoint="WR_DR_history_menu",
                req_type=RequestType.TR.value,
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Заявки в клининг",
            callback_data=PageCallbackData(
                page=0,
                requests_endpoint="WR_DR_history_menu",
                req_type=RequestType.CR.value,
            ).pack(),
        ),
        InlineKeyboardButton(
            text=text.back,
            callback_data=department_kb.wr_menu_button.callback_data,
        ),
    ]
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тип заявок") + "\nИстория",
        reply_markup=kb.create_inline_keyboard(*buttons),
    )


@router.callback_query(
    PageCallbackData.filter(F.requests_endpoint == "WR_DR_history_menu")
)
async def show_worker_history_menu(
    callback: CallbackQuery,
    callback_data: PageCallbackData,
):
    reply_markup = (
        department_kb.create_kb_with_end_point_TR(
            end_point="WR_DR_show_form_history",
            menu_button=department_kb.wr_history,
            requests=get_all_history_technical_requests_for_worker(
                tg_id=callback.message.chat.id,
                page=callback_data.page,
            ),
            page=callback_data.page,
            requests_endpoint="WR_DR_show_form_history",
        )
        if callback_data.req_type == RequestType.TR.value
        else department_kb.create_kb_with_end_point_CR(
            end_point="WR_DR_show_form_history",
            menu_button=department_kb.wr_history,
            requests=get_all_history_cleaning_requests_for_worker(
                tg_id=callback.message.chat.id,
                page=callback_data.page,
            ),
            page=callback_data.page,
            requests_endpoint="WR_DR_show_form_history",
        )
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("История заявок"),
        reply_markup=reply_markup,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "WR_DR_show_form_history")
)
async def show_worker_history_form(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = []
    if callback_data.req_type == RequestType.TR.value:
        await show_form_technician(
            callback=callback,
            callback_data=callback_data,
            state=state,
            buttons=buttons,
            history_or_waiting_button=department_kb.wr_history,
        )
    else:
        await show_form_cleaning(
            callback=callback,
            callback_data=callback_data,
            state=state,
            buttons=buttons,
            history_or_waiting_button=department_kb.wr_history,
        )


@router.callback_query(F.data == "send_WR_TR_CR")
async def save_worker_request(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    problem_name = data.get("problem_name")
    description = data.get("description")
    department_name = data.get("dep_name")
    problem_group = data.get("problem_group")

    if problem_group is None:
        logger.error("Problem group in department request is None")
    else:
        photo = data["photo"]
        photo_files: list[UploadFile] = []
        for doc in photo:
            photo_files.append(await download_file(doc))
        message = callback.message

    if problem_group == "TR":
        if not await create_technical_request(
            problem_name=problem_name,
            description=description,
            photo_files=photo_files,
            telegram_id=callback.message.chat.id,
            department_name=department_name,
        ):
            message = await try_edit_or_answer(
                message=callback.message,
                text=text.err,
                return_message=True,
            )
            await sleep(2)
            await try_delete_message(message=message)
    else:
        if not await create_cleaning_request(
            problem_name=problem_name,
            description=description,
            photo_files=photo_files,
            telegram_id=callback.message.chat.id,
            department_name=department_name,
        ):
            message = await try_edit_or_answer(
                message=callback.message,
                text=text.err,
                return_message=True,
            )
            await sleep(2)
            await try_delete_message(message=message)

    await state.clear()
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=message,
        text=hbold(department_kb.wr_menu_button.text),
        reply_markup=department_kb.wr_menu,
    )
