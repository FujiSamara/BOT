from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaDocument,
    BufferedInputFile,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from fastapi import UploadFile

from bot import text
from bot.states import (
    Base,
    RepairmanTechnicalRequestForm,
    WorkerTechnicalRequestForm,
)
from bot.kb import (
    create_inline_keyboard,
    worker_tech_req_menu_button,
    worker_tech_req_menu,
    worker_tech_req_waiting,
    worker_tech_req_history,
    kru_tech_req_menu_button,
    kru_tech_req_menu,
    tech_req_create,
    worker_create_tech_req_kb,
    create_reply_keyboard,
    repairman_tech_req_menu_button,
    repairman_tech_req_menu,
    repairman_tech_req_waiting,
    repairman_repair_tech_req_kb,
    repairman_tech_req_history,
)
from bot.handlers.utils import (
    notify_worker_by_telegram_id,
    try_edit_or_answer,
    try_delete_message,
    download_file,
    handle_documents_form,
    handle_documents,
)
from bot.handlers.tech_req.utils import (
    create_keybord_with_end_point,
)
from bot.handlers.tech_req.schemas import ShowRequestCallbackData

from db.service import (
    get_all_history_technical_requests_by_repairman_TG_and_department_id,
    get_all_history_technical_requests_by_worker_TG_id,
    get_all_waiting_technical_requests_by_repairman_TG_id_and_department_id,
    get_all_waiting_technical_requests_by_worker_TG_id,
    get_technical_problem_names,
    create_technical_request,
    get_technical_request_by_id,
    update_technical_request_repairman,
)
from db.models import ApprovalStatus


router = Router(name="technical_request")


@router.callback_query(F.data == worker_tech_req_menu_button.callback_data)
async def worker_menu(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=worker_tech_req_menu,
    )


@router.callback_query(F.data == tech_req_create.callback_data)
async def worker_create_request_cb(callback: CallbackQuery, state: FSMContext):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Создать заявку"),
        reply_markup=await worker_create_tech_req_kb(state),
    )


async def worker_create_request_ms(message: CallbackQuery, state: FSMContext):
    await try_edit_or_answer(
        message=message,
        text=hbold("Создать заявку"),
        reply_markup=await worker_create_tech_req_kb(state),
    )


@router.callback_query(F.data == "problem_type_tech_req")
async def get_problem(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerTechnicalRequestForm.problem_name)
    problems = get_technical_problem_names()
    problems.sort()
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите проблему:"),
        reply_markup=create_reply_keyboard(
            "⏪ Назад", *[problem for problem in problems]
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

    if message.text == "⏪ Назад":
        await worker_create_request_ms(message, state)
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
        await worker_create_request_ms(message, state)


@router.callback_query(F.data == "description_tech_req")
async def get_description(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerTechnicalRequestForm.description)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(text=hbold("Введите описание проблемы:"))
    await state.update_data(msg=msg)


@router.message(WorkerTechnicalRequestForm.description)
async def set_description(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await state.update_data(description=message.text)
    await try_delete_message(message)
    await worker_create_request_ms(message, state)


@router.callback_query(F.data == "photo_tech_req")
async def get_worker_photo(callback: CallbackQuery, state: FSMContext):
    await handle_documents_form(
        callback.message, state, WorkerTechnicalRequestForm.photo
    )


@router.message(WorkerTechnicalRequestForm.photo)
async def set_worekr_photo(message: Message, state: FSMContext):
    await handle_documents(message, state, "photo", worker_create_request_ms)


@router.callback_query(F.data == "send_worker_tech_req")
async def save_worker_request(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    problem_name = data["problem_name"]
    description = data["description"]

    photo = data["photo"]
    photo_files: list[UploadFile] = []
    for doc in photo:
        photo_files.append(await download_file(doc))

    repairman_TG_id = create_technical_request(
        problem_name=problem_name,
        description=description,
        photo_files=photo_files,
        telegram_id=callback.message.chat.id,
    )

    await notify_worker_by_telegram_id(
        id=repairman_TG_id, message=text.notifay_repairman
    )

    await state.clear()
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=worker_tech_req_menu,
    )


@router.callback_query(F.data == worker_tech_req_waiting.callback_data)
async def worker_waiting(callback: CallbackQuery):
    requests = get_all_waiting_technical_requests_by_worker_TG_id(
        telegram_id=callback.message.chat.id
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Ожидающие заявки"),
        reply_markup=create_keybord_with_end_point(
            end_point="worker_show_form_waiting",
            menu_button=worker_tech_req_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "worker_show_form_waiting")
)
async def worker_show_form_waiting(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = []
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_button=worker_tech_req_waiting,
    )


@router.callback_query(F.data == worker_tech_req_history.callback_data)
async def worker_history(callback: CallbackQuery):
    requests = get_all_history_technical_requests_by_worker_TG_id(
        telegram_id=callback.message.chat.id
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("История заявок"),
        reply_markup=create_keybord_with_end_point(
            end_point="worker_show_form_history",
            menu_button=worker_tech_req_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "worker_show_form_history")
)
async def worker_show_form_history(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = []
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_button=worker_tech_req_history,
    )


@router.callback_query(F.data == repairman_tech_req_menu_button.callback_data)
async def repairman_menu(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=repairman_tech_req_menu,
    )


@router.callback_query(F.data == repairman_tech_req_history.callback_data)
async def repairman_history(callback: CallbackQuery, state):
    requests = get_all_history_technical_requests_by_repairman_TG_and_department_id(
        telegram_id=callback.message.chat.id
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("История заявок"),
        reply_markup=create_keybord_with_end_point(
            end_point="repairman_show_form_history",
            menu_button=repairman_tech_req_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "repairman_show_form_history")
)
async def repairman_show_form_history(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = []
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_button=repairman_tech_req_history,
    )


@router.callback_query(F.data == repairman_tech_req_waiting.callback_data)
async def repairman_waiting(callback: CallbackQuery):
    requests = get_all_waiting_technical_requests_by_repairman_TG_id_and_department_id(
        telegram_id=callback.message.chat.id
    )
    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Ожидающие заявки"),
        reply_markup=create_keybord_with_end_point(
            end_point="repairman_show_form_waiting",
            menu_button=repairman_tech_req_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "repairman_show_form_waiting")
)
async def repairman_show_form_waiting(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Выполнить заявку",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="repairman_repair_form",
                ).pack(),
            )
        ]
    ]
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_button=repairman_tech_req_waiting,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "repairman_repair_form")
)
async def repairman_repair_form_cb(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Выполнить заявку"),
        reply_markup=await repairman_repair_tech_req_kb(
            state=state, callback_data=callback_data
        ),
    )


async def repairman_repair_form_ms(message: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Выполнить заявку"),
        reply_markup=await repairman_repair_tech_req_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="repairman_repair_form",
            ),
        ),
    )


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "get_photo"))
async def get_repairman_photo(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.update_data(request_id=callback_data.request_id)
    await handle_documents_form(
        callback.message, state, RepairmanTechnicalRequestForm.photo
    )


@router.message(RepairmanTechnicalRequestForm.photo)
async def set_repairman_photo(message: Message, state: FSMContext):
    await handle_documents(message, state, "photo", repairman_repair_form_ms)


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "save_repairman_repair")
)
async def save_repairman_repair(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    data = await state.get_data()

    photo = data["photo"]
    photo_files: list[UploadFile] = []
    for doc in photo:
        photo_files.append(await download_file(doc))

    teritorial_manager_id = update_technical_request_repairman(
        photo_files=photo_files, request_id=callback_data.request_id
    )

    await notify_worker_by_telegram_id(
        id=teritorial_manager_id, message=text.notifay_teritorial_manager
    )

    await state.clear()
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=repairman_tech_req_menu,
    )


@router.callback_query(F.data == kru_tech_req_menu_button.callback_data)
async def kru_menu(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=kru_tech_req_menu,
    )


async def show_form(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: ShowRequestCallbackData,
    history_button: InlineKeyboardButton,
    buttons: list[list[InlineKeyboardButton]],
):
    data = await state.get_data()
    if "msgs" in data:
        for msg in data["msgs"]:
            await try_delete_message(msg)
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
            text += "В процессе выполнения."
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
            text += (
                f"Дата переоткрытия заявки {request.reopen_date.strftype("%d.%m.%Y")}."
            )

    buttons.append(
        [InlineKeyboardButton(text="Назад", callback_data=history_button.callback_data)]
    )

    buttons.append(
        [
            InlineKeyboardButton(
                text="Фотографии поломки",
                callback_data=ShowRequestCallbackData(
                    request_id=request.id,
                    end_point="problem_docs",
                    last_end_point=callback_data.end_point,
                ).pack(),
            )
        ]
    )

    if request.state == ApprovalStatus.pending_approval:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Фотогарфии ремонта",
                    callback_data=ShowRequestCallbackData(
                        request_id=request.id,
                        end_point="repair_docs",
                        last_end_point=callback_data.end_point,
                    ).pack(),
                )
            ]
        )

    keybord = InlineKeyboardMarkup(inline_keyboard=buttons)
    await try_edit_or_answer(message=callback.message, text=text, reply_markup=keybord)


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "problem_docs"))
async def problem_documents(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    media: list[InputMediaDocument] = []
    request = get_technical_request_by_id(callback_data.request_id)
    for photo in request.problem_photos:
        media.append(
            InputMediaDocument(
                media=BufferedInputFile(
                    file=await photo.document.read(), filename=photo.document.filename
                )
            )
        )
    await send_photos(
        callback=callback,
        state=state,
        callback_data=callback_data,
        media=media,
        request_id=request.id,
    )


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "repair_docs"))
async def repair_documents(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    media: list[InputMediaDocument] = []
    request = get_technical_request_by_id(callback_data.request_id)
    for photo in request.repair_photos:
        media.append(
            InputMediaDocument(
                media=BufferedInputFile(
                    file=await photo.document.read(), filename=photo.document.filename
                )
            )
        )
    await send_photos(
        callback=callback,
        state=state,
        callback_data=callback_data,
        media=media,
        request_id=request.id,
    )


async def send_photos(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: ShowRequestCallbackData,
    media: list[InputMediaDocument],
    request_id: int,
):
    await try_delete_message(callback.message)
    msgs = await callback.message.answer_media_group(media=media)
    await state.update_data(msgs=msgs)
    await msgs[0].reply(
        text=hbold("Выберите действие:"),
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text="Назад",
                callback_data=ShowRequestCallbackData(
                    request_id=request_id,
                    end_point=callback_data.last_end_point,
                ).pack(),
            )
        ),
    )
