from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaDocument,
    BufferedInputFile
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from fastapi import UploadFile
from settings import get_settings
from bot.handlers.tech_req.schemas import(
    ShowRequestCallbackData,
)
from db.models import ApprovalStatus
from bot.handlers import utils
from bot.handlers.utils import (
    try_edit_or_answer,
    handle_documents_form,
    handle_documents
)
from bot.kb import (
    create_inline_keyboard,
    tech_req_menu_button,
    tech_req_menu,
    tech_req_create,
    tech_req_waiting,
    tech_req_history,
    create_tech_req_kb,
    create_reply_keyboard,
)
from bot.states import (
    Base,
    TechRequestForm,
)
from db.service import(
    get_all_technical_requests_by_TG_id,
    get_all_waiting_technical_requests_by_TG_id,
    get_technical_problem_names,
    create_technical_request,
    get_technical_request_by_id,
)
from bot import text


router = Router(name="technical_request")


@router.callback_query(F.data == tech_req_menu_button.callback_data)
async def menu(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message, text=hbold("Тех. заявки"), reply_markup=tech_req_menu
    )


@router.callback_query(F.data == tech_req_create.callback_data)
async def create_menu_cb(callback: CallbackQuery, state: FSMContext):
    await try_edit_or_answer(
        message=callback.message, text=hbold("Создать заявку"), reply_markup=await create_tech_req_kb(state)
    )


async def create_menu_ms(message: CallbackQuery, state: FSMContext):
    await try_edit_or_answer(
        message=message, text=hbold("Создать заявку"), reply_markup=await create_tech_req_kb(state)
    )


@router.callback_query(F.data == "problem_type_tech_req")
async def get_problem(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TechRequestForm.problem_name)
    problems = get_technical_problem_names()
    problems.sort()
    await utils.try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите проблему:"),
        reply_markup=create_reply_keyboard("⏪ Назад", *[problem for problem in problems]),
    )
    await state.update_data(msg=msg)


@router.message(TechRequestForm.problem_name)
async def set_problem(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await utils.try_delete_message(msg)
    await utils.try_delete_message(message)

    if message.text == "⏪ Назад":
        await create_menu_ms(message, state)
    else:
        problems = get_technical_problem_names()
        if message.text not in problems:
            problems.sort()
            msg = await message.answer(
                text=text.format_err,
                reply_markup=create_reply_keyboard(*[problem for problem in problems]),
            )
            await state.update_data(msg=msg)
            return
        await state.update_data(problem_name=message.text)
        await create_menu_ms(message, state)


@router.callback_query(F.data == "description_tech_req")
async def get_description(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TechRequestForm.description)
    await utils.try_delete_message(callback.message)
    msg = await callback.message.answer(text=hbold("Введите описание проблемы:"))
    await state.update_data(msg=msg)


@router.message(TechRequestForm.description)
async def set_description(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await utils.try_delete_message(msg)
    await state.update_data(description=message.text)
    await utils.try_delete_message(message)
    await create_menu_ms(message, state)


@router.callback_query(F.data == "photo_tech_req")
async def get_photo(callback: CallbackQuery, state: FSMContext):
   await handle_documents_form(callback.message, state, TechRequestForm.photo)


@router.message(TechRequestForm.photo)
async def set_photo(message: Message, state: FSMContext):
    await handle_documents(message, state, "photo", create_menu_ms)


@router.callback_query(F.data == "send_tech_req")
async def save_worker_request(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    problem_name = data["problem_name"]
    description = data["description"]

    photo = data["photo"]
    photo_files: list[UploadFile] = []
    for doc in photo:
        photo_files.append(await utils.download_file(doc))

    create_technical_request(
        problem_name = problem_name,
        description = description,
        photo_files = photo_files,
        state =  ApprovalStatus.pending,
        telegram_id = callback.message.chat.id
    )

    await state.clear()
    await state.set_state(Base.none)
    await utils.try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_req_menu,
    )


@router.callback_query(F.data == tech_req_waiting.callback_data)
async def waiting(callback: CallbackQuery):
    await utils.try_delete_message(callback.message)
    requests = get_all_waiting_technical_requests_by_TG_id(telegram_id=callback.message.chat.id)

    buttons: list[InlineKeyboardButton] = []
    if len(requests) > 0:
        for request in requests:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text = request.open_date.date().strftime(get_settings().date_format),
                        callback_data=ShowRequestCallbackData(
                            request_id = request.id,
                            end_point = "show_form"
                        ).pack()
                    )
                ]
            )

    buttons.append([tech_req_menu_button])
    keybord = InlineKeyboardMarkup(inline_keyboard=buttons)
    await try_edit_or_answer(
        message=callback.message, text=hbold("История заявок"),
        reply_markup=keybord
    )


@router.callback_query(F.data == tech_req_history.callback_data)
async def history(callback: CallbackQuery):
    await utils.try_delete_message(callback.message)
    requests = get_all_technical_requests_by_TG_id(telegram_id=callback.message.chat.id)

    buttons: list[InlineKeyboardButton] = []
    try:
        for request in requests:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text = request.open_date.date().strftime(get_settings().date_format),
                        callback_data=ShowRequestCallbackData(
                            request_id = request.id,
                            end_point = "show_form"
                        ).pack()
                    )
                ]
            )
    finally:
        buttons.append([tech_req_menu_button])
        keybord = InlineKeyboardMarkup(inline_keyboard=buttons)

    await try_edit_or_answer(
        message=callback.message, text=hbold("История заявок"),
        reply_markup=keybord
    )


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "show_form"))
async def show_form(callback: CallbackQuery, state:FSMContext, callback_data: ShowRequestCallbackData):
    data = await state.get_data()
    if "msgs" in data:
        for msg in data["msgs"]:
            await utils.try_delete_message(msg)
        await state.update_data(msgs=[])
    
    request = get_technical_request_by_id(callback_data.request_id)
    text = f"{hbold(request.problem.problem_name)} от {request.open_date.date()}. \n\
Описание:\n{request.description} \n\
Адресс: {request.worker.department.address}\n\
ФИО сотрудника: {request.worker.l_name} {request.worker.f_name} {request.worker.o_name}.\n\
ФИО исполнителя: {request.repairman.l_name} {request.repairman.f_name} {request.repairman.o_name}.\n\
Статус: "
    
    match request.state:
        case ApprovalStatus.approved:
            text += "Выполенно."
        case ApprovalStatus.pending:
            text += "В процессе выполнение."
        case ApprovalStatus.pending_approval:
            text += "Ожидание оценки от ТУ."
        case ApprovalStatus.denied:
            text += "Отправленно на доработку."
    text += "\n"

    if request.confirmation_date:
        text += f"Дата утверждения проделанной работы {request.confirmation_date.strftype("%d.%m.%Y")}.\n"
        if request.close_date:
            text += f"Дата закрытия заявки {request.close_date.strftype("%d.%m.%Y")}.\n"
        if request.reopen_date:
            text += f"Дата переоткрытия заявки {request.reopen_date.strftype("%d.%m.%Y")}."
    
    buttons: list[InlineKeyboardButton] = [
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=tech_req_history.callback_data
            )
        ]
    ]

    #TODO кнопки для исполнителя и ТУ

    buttons.append(
        [
            InlineKeyboardButton(
                text="Показать документы",
                callback_data=ShowRequestCallbackData(
                    request_id = request.id,
                    end_point = "docs"
                ).pack()
            )
        ]
    )
    
    keybord = InlineKeyboardMarkup(inline_keyboard=buttons)
    await try_edit_or_answer(
        message=callback.message,
        text=text,
        reply_markup=keybord
    )

@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "docs"))
async def documents(callback: CallbackQuery, state:FSMContext, callback_data: ShowRequestCallbackData):
    media: list[InputMediaDocument] = []
    request = get_technical_request_by_id(callback_data.request_id)
    for photo in request.photos:
        media.append(
            InputMediaDocument(
                media=BufferedInputFile(
                    file=await photo.document.read(), filename=photo.document.filename
                )
            )
        )

    await utils.try_delete_message(callback.message)
    msgs = await callback.message.answer_media_group(media=media)
    await state.update_data(msgs=msgs)
    await msgs[0].reply(
        text=hbold("Выберите действие:"),
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text="Назад",
                callback_data=ShowRequestCallbackData(
                    request_id = request.id,
                    end_point = "show_form"
                ).pack(),
            )
        ),
    )