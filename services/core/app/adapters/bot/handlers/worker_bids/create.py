from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    BufferedInputFile,
    InputMediaDocument,
)
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext

from fastapi import UploadFile
import app.adapters.bot.kb as kb
from app.adapters.bot.handlers import utils
from app.adapters.bot.states import WorkerBidCreating, Base
from app import services
from app.adapters.bot.handlers.worker_bids.schemas import (
    BidViewMode,
    WorkerBidCallbackData,
)
from app.adapters.bot.handlers.worker_bids.utils import (
    get_worker_bid_list_info,
    get_full_worker_bid_info,
)
import app.adapters.bot.text as text


router = Router(name="create_worker_bid")


@router.callback_query(F.data == "get_worker_bid_menu")
async def get_form(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Base.none)
    await utils.try_edit_or_answer(
        message=callback.message,
        text=hbold("Согласование кандидатов"),
        reply_markup=kb.worker_bid_menu,
    )


async def send_create_menu(message: Message, state: FSMContext):
    await state.set_state(Base.none)
    await utils.try_edit_or_answer(
        message=message,
        text=hbold("Согласование кандидатов"),
        reply_markup=await kb.get_create_worker_bid_menu(state),
    )


@router.callback_query(F.data == "get_create_worker_bid_menu")
async def get_menu(callback: CallbackQuery, state: FSMContext):
    await send_create_menu(callback.message, state)


@router.callback_query(F.data == "send_worker_bid")
async def save_worker_bid(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    f_name = data["f_name"]
    l_name = data["l_name"]
    o_name = data["o_name"]
    post = data["post"]
    department = data["department"]
    worksheet = data["worksheet"]
    passport = data["passport"]
    work_permission = data.get("work_permission")
    if not work_permission:
        work_permission = []

    worksheet_files: list[UploadFile] = []
    passport_files: list[UploadFile] = []
    work_permission_files: list[UploadFile] = []

    for doc in worksheet:
        worksheet_files.append(await utils.download_file(doc))
    for doc in passport:
        passport_files.append(await utils.download_file(doc))
    for doc in work_permission:
        work_permission_files.append(await utils.download_file(doc))

    services.create_worker_bid(
        f_name,
        l_name,
        o_name,
        post,
        department,
        worksheet_files,
        passport_files,
        work_permission_files,
        callback.message.chat.id,
    )
    await state.clear()
    await state.set_state(Base.none)
    await utils.try_edit_or_answer(
        message=callback.message,
        text=hbold("Согласование кандидатов"),
        reply_markup=kb.worker_bid_menu,
    )


# First name
@router.callback_query(F.data == "get_worker_bid_fname_form")
async def get_fname_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerBidCreating.f_name)
    await utils.try_delete_message(callback.message)
    msg = await callback.message.answer(text=hbold("Введите имя:"))
    await state.update_data(msg=msg)


@router.message(WorkerBidCreating.f_name)
async def set_fname(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await utils.try_delete_message(msg)
    await state.update_data(f_name=message.text)
    await utils.try_delete_message(message)
    await send_create_menu(message, state)


# Last name
@router.callback_query(F.data == "get_worker_bid_lname_form")
async def get_lname_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerBidCreating.l_name)
    await utils.try_delete_message(callback.message)
    msg = await callback.message.answer(text=hbold("Введите фамилию:"))
    await state.update_data(msg=msg)


@router.message(WorkerBidCreating.l_name)
async def set_lname(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await utils.try_delete_message(msg)
    await state.update_data(l_name=message.text)
    await utils.try_delete_message(message)
    await send_create_menu(message, state)


# Patronymic
@router.callback_query(F.data == "get_worker_bid_oname_form")
async def get_oname_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerBidCreating.o_name)
    await utils.try_delete_message(callback.message)
    msg = await callback.message.answer(text=hbold("Введите отчество:"))
    await state.update_data(msg=msg)


@router.message(WorkerBidCreating.o_name)
async def set_oname(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await utils.try_delete_message(msg)
    await state.update_data(o_name=message.text)
    await utils.try_delete_message(message)
    await send_create_menu(message, state)


# Post
@router.callback_query(F.data == "get_worker_bid_post_form")
async def get_post_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerBidCreating.post)
    posts = services.get_posts_names()
    posts.sort()
    await utils.try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите должность:"),
        reply_markup=kb.create_reply_keyboard(*[post for post in posts]),
    )
    await state.update_data(msg=msg)


@router.message(WorkerBidCreating.post)
async def set_post(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await utils.try_delete_message(msg)
    posts = services.get_posts_names()
    await utils.try_delete_message(message)
    if message.text not in posts:
        posts.sort()
        msg = await message.answer(
            text=text.format_err,
            reply_markup=kb.create_reply_keyboard(*[post for post in posts]),
        )
        await state.update_data(msg=msg)
        return
    await state.update_data(post=message.text)
    await send_create_menu(message, state)


# Departments
@router.callback_query(F.data == "get_worker_bid_department_form")
async def get_department_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerBidCreating.department)
    departments = services.get_departments_names()
    departments.sort()
    await utils.try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите предприятие:"),
        reply_markup=kb.create_reply_keyboard(*[post for post in departments]),
    )
    await state.update_data(msg=msg)


@router.message(WorkerBidCreating.department)
async def set_department(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await utils.try_delete_message(msg)
    departments = services.get_departments_names()
    await utils.try_delete_message(message)
    if message.text not in departments:
        departments.sort()
        msg = await message.answer(
            text=text.format_err,
            reply_markup=kb.create_reply_keyboard(*[post for post in departments]),
        )
        await state.update_data(msg=msg)
        return
    await state.update_data(department=message.text)
    await send_create_menu(message, state)


# Documents
# Worksheet
@router.callback_query(F.data == "get_worker_bid_worksheet_form")
async def get_worksheet_form(callback: CallbackQuery, state: FSMContext):
    await utils.handle_documents_form(
        callback.message, state, WorkerBidCreating.worksheet
    )


@router.message(WorkerBidCreating.worksheet)
async def set_worksheet(message: Message, state: FSMContext):
    await utils.handle_documents(message, state, "worksheet", send_create_menu)


# Passport
@router.callback_query(F.data == "get_worker_bid_passport_form")
async def get_passport_form(callback: CallbackQuery, state: FSMContext):
    await utils.handle_documents_form(
        callback.message, state, WorkerBidCreating.passport
    )


@router.message(WorkerBidCreating.passport)
async def set_passport(message: Message, state: FSMContext):
    await utils.handle_documents(message, state, "passport", send_create_menu)


# Work permission
@router.callback_query(F.data == "get_worker_bid_work_permission_form")
async def get_work_permission_form(callback: CallbackQuery, state: FSMContext):
    await utils.handle_documents_form(
        callback.message, state, WorkerBidCreating.work_permission
    )


@router.message(WorkerBidCreating.work_permission)
async def set_work_permission(message: Message, state: FSMContext):
    await utils.handle_documents(message, state, "work_permission", send_create_menu)


# History
@router.callback_query(
    WorkerBidCallbackData.filter(F.mode == BidViewMode.full),
    WorkerBidCallbackData.filter(F.endpoint_name == "documents"),
)
async def get_documents(
    callback: CallbackQuery, callback_data: WorkerBidCallbackData, state: FSMContext
):
    bid = services.get_worker_bid_by_id(callback_data.id)
    media: list[InputMediaDocument] = []
    for doc in bid.worksheet:
        media.append(
            InputMediaDocument(
                media=BufferedInputFile(
                    file=await doc.document.read(), filename=doc.document.filename
                )
            )
        )
    for doc in bid.passport:
        media.append(
            InputMediaDocument(
                media=BufferedInputFile(
                    file=await doc.document.read(), filename=doc.document.filename
                )
            )
        )
    for doc in bid.work_permission:
        media.append(
            InputMediaDocument(
                media=BufferedInputFile(
                    file=await doc.document.read(), filename=doc.document.filename
                )
            )
        )

    await utils.try_delete_message(callback.message)
    msgs = await callback.message.answer_media_group(media=media)
    await state.update_data(msgs=msgs)
    await msgs[0].reply(
        text=hbold("Выберите действие:"),
        reply_markup=kb.create_inline_keyboard(
            InlineKeyboardButton(
                text="Назад",
                callback_data=WorkerBidCallbackData(
                    id=bid.id,
                    mode=callback_data.mode,
                    endpoint_name="bid",
                ).pack(),
            )
        ),
    )


@router.callback_query(
    WorkerBidCallbackData.filter(F.mode == BidViewMode.full),
    WorkerBidCallbackData.filter(F.endpoint_name == "bid"),
)
async def get_worker_bid(
    callback: CallbackQuery, callback_data: WorkerBidCallbackData, state: FSMContext
):
    bid_id = callback_data.id
    bid = services.get_worker_bid_by_id(bid_id)
    data = await state.get_data()
    if "msgs" in data:
        for msg in data["msgs"]:
            await utils.try_delete_message(msg)
        await state.update_data(msgs=[])

    caption = get_full_worker_bid_info(bid)

    await utils.try_edit_message(
        message=callback.message,
        text=caption,
        reply_markup=kb.create_inline_keyboard(
            kb.worker_bid_history_button,
            InlineKeyboardButton(
                text="Показать документы",
                callback_data=WorkerBidCallbackData(
                    id=bid.id,
                    mode=callback_data.mode,
                    endpoint_name="documents",
                ).pack(),
            ),
        ),
    )


@router.callback_query(F.data == "get_worker_bid_history")
async def get_workers_bids_history(callback: CallbackQuery):
    bids = services.get_workers_bids_by_sender_telegram_id(callback.message.chat.id)
    bids = sorted(bids, key=lambda bid: bid.create_date, reverse=True)[:10]
    keyboard = kb.create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_worker_bid_list_info(bid),
                callback_data=WorkerBidCallbackData(
                    id=bid.id, mode=BidViewMode.full, endpoint_name="bid"
                ).pack(),
            )
            for bid in bids
        ),
        kb.worker_bid_menu_button,
    )
    await utils.try_delete_message(callback.message)
    await callback.message.answer("История заявок:", reply_markup=keyboard)
