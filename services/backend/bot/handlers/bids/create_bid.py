from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    Message,
    BufferedInputFile,
    ReplyKeyboardRemove,
    InputMediaDocument,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
import asyncio

from fastapi import UploadFile

# bot imports
from bot.kb import (
    bid_menu,
    get_create_bid_menu,
    payment_type_menu,
    settings_bid_menu_button,
    create_bid_menu_button,
    create_inline_keyboard,
    create_reply_keyboard,
    InlineKeyboardButton,
    bid_create_history_button,
    bid_create_pending_button,
    bid_create_search_button,
)

from bot.text import format_err, payment_types, bid_create_greet, back

from bot.states import BidCreating, Base
from bot.handlers.bids.schemas import (
    BidCallbackData,
    BidViewMode,
    BidViewType,
)

from bot.handlers.bids.utils import (
    get_full_bid_info,
    get_short_bid_info,
    get_bid_list_info,
)
from bot.handlers.utils import (
    try_delete_message,
    try_edit_or_answer,
    try_edit_message,
    download_file,
    handle_documents_form,
    handle_documents,
)

# db imports
from db.service import (
    get_departments_names,
    create_bid,
    get_bids_by_worker_telegram_id,
    get_bid_by_id,
    get_pending_bids_by_worker_telegram_id,
    get_chapters,
    get_expenditures_names_by_chapter,
    find_bid_for_worker,
)
from db.models import ApprovalStatus


router = Router(name="bid_creating")


async def clear_state_with_success(
    message: Message, state: FSMContext, sleep_time=1, edit=False
):
    ans = await message.answer(hbold("Успешно!"), reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(sleep_time)
    await ans.delete()
    await state.set_state(Base.none)
    if edit:
        await try_edit_message(
            message=message,
            text=hbold(bid_create_greet),
            reply_markup=await get_create_bid_menu(state),
        )
    else:
        await message.answer(
            hbold(bid_create_greet), reply_markup=await get_create_bid_menu(state)
        )


# Create section
@router.callback_query(F.data == "get_bid_settings_menu")
async def get_settings_form(callback: CallbackQuery, state: FSMContext):
    await clear_state_with_success(callback.message, state, sleep_time=0, edit=True)


@router.callback_query(F.data == "send_bid")
async def send_bid(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(Base.none)
    amount = data["amount"]
    payment_type = data["type"]
    department = data["department"]
    purpose = data["purpose"]
    comment = data.get("comment")
    documents = data["document"]
    expenditure = data["expenditure"]
    need_edm = data.get("need_edm")
    activity_type = data.get("activity_type")

    document_files: list[UploadFile] = []

    for doc in documents:
        document_files.append(await download_file(doc))

    fac_state = ApprovalStatus.pending_approval
    cc_state = ApprovalStatus.pending
    paralegal_state = ApprovalStatus.pending
    kru_state = ApprovalStatus.pending
    owner_state = ApprovalStatus.pending
    if int(amount) <= 30000:
        owner_state = ApprovalStatus.skipped
    accountant_card_state = ApprovalStatus.pending
    accountant_cash_state = ApprovalStatus.pending
    teller_card_state = ApprovalStatus.pending
    teller_cash_state = ApprovalStatus.pending

    if payment_type == "card":
        accountant_cash_state = ApprovalStatus.skipped
        teller_cash_state = ApprovalStatus.skipped
    else:
        accountant_card_state = ApprovalStatus.skipped
        teller_card_state = ApprovalStatus.skipped
        paralegal_state = ApprovalStatus.skipped

    await create_bid(
        amount=amount,
        payment_type=payment_type,
        department=department,
        files=document_files,
        purpose=purpose,
        comment=comment,
        expenditure=expenditure,
        telegram_id=callback.message.chat.id,
        fac_state=fac_state,
        cc_state=cc_state,
        paralegal_state=paralegal_state,
        kru_state=kru_state,
        owner_state=owner_state,
        accountant_card_state=accountant_card_state,
        accountant_cash_state=accountant_cash_state,
        teller_card_state=teller_card_state,
        teller_cash_state=teller_cash_state,
        need_edm=need_edm,
        activity_type=activity_type,
    )

    await try_edit_message(message=callback.message, text="Успешно!")
    await asyncio.sleep(1)
    await try_edit_message(
        message=callback.message,
        text=hbold(create_bid_menu_button.text),
        reply_markup=bid_menu,
    )
    await state.clear()


# Amount section
@router.callback_query(F.data == "get_amount_form")
async def get_amount_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.payment_amount)
    await try_edit_message(message=callback.message, text="Успешно!")
    await try_edit_message(
        message=callback.message,
        text=hbold("Введите требуемую сумму:"),
        reply_markup=create_inline_keyboard(settings_bid_menu_button),
    )


@router.message(BidCreating.payment_amount)
async def set_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.html_text)
        await state.update_data(amount=str(amount))
        await clear_state_with_success(message, state)
    except Exception:
        await message.answer(
            format_err, reply_markup=create_inline_keyboard(settings_bid_menu_button)
        )


# Payment type section
@router.callback_query(F.data == "get_paymant_form")
async def get_amount_type_form(callback: CallbackQuery):
    await try_edit_message(
        message=callback.message,
        text=hbold("Выберите тип оплаты:"),
        reply_markup=payment_type_menu,
    )


@router.callback_query(F.data.in_(payment_types))
async def set_amount_type(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type=callback.data)
    await clear_state_with_success(callback.message, state, edit=True)


# Department section
@router.callback_query(F.data == "get_department_form")
async def get_department_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.department)
    dep = get_departments_names()
    await try_delete_message(callback.message)
    await callback.message.answer(
        hbold("Выберите предприятие:"),
        reply_markup=create_reply_keyboard("⏪ Назад", *dep),
    )


@router.message(BidCreating.department)
async def set_department_type(message: Message, state: FSMContext):
    dep = get_departments_names()
    if message.text == "⏪ Назад":
        await clear_state_with_success(message, state, sleep_time=0)
    elif message.text in dep:
        await state.update_data(department=message.text)
        await clear_state_with_success(message, state)
    else:
        await message.answer(format_err)


# Expenditure section
async def send_expenditre_chapter_form(message: Message, state: FSMContext):
    await state.set_state(BidCreating.expenditure_chapter)
    chapters = get_chapters()
    await try_delete_message(message)
    await message.answer(
        hbold("Выберите раздел:"),
        reply_markup=create_reply_keyboard("⏪ Назад", *chapters),
    )


@router.callback_query(F.data == "get_expenditure_chapter_form")
async def get_expenditure_chapter_form(callback: CallbackQuery, state: FSMContext):
    await send_expenditre_chapter_form(callback.message, state)


async def get_expenditure_form(message: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.expenditure)
    data = await state.get_data()
    exps = get_expenditures_names_by_chapter(data["chapter"])
    await try_delete_message(message)
    await message.answer(
        hbold("Выберите статью:"),
        reply_markup=create_reply_keyboard("⏪ Назад", *exps),
    )


@router.message(BidCreating.expenditure)
async def set_expenditure(message: Message, state: FSMContext):
    data = await state.get_data()
    exps = get_expenditures_names_by_chapter(data["chapter"])
    if message.text == "⏪ Назад":
        await send_expenditre_chapter_form(message, state)
    elif message.text in exps:
        await state.update_data(expenditure=message.text)
        await clear_state_with_success(message, state)
    else:
        await message.answer(format_err)


@router.message(BidCreating.expenditure_chapter)
async def set_expenditure_chapter(message: Message, state: FSMContext):
    chapters = get_chapters()
    if message.text == "⏪ Назад":
        await clear_state_with_success(message, state, sleep_time=0)
    elif message.text in chapters:
        await state.update_data(chapter=message.text)
        await get_expenditure_form(message, state)
    else:
        await message.answer(format_err)


# Purpose section
@router.callback_query(F.data == "get_purpose_form")
async def get_purpose_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.payment_purpose)
    await try_edit_message(
        message=callback.message, text=hbold("Введите цель платежа:")
    )


@router.message(BidCreating.payment_purpose)
async def set_purpose(message: Message, state: FSMContext):
    await state.update_data(purpose=message.html_text)
    await clear_state_with_success(message, state)


# Comment
@router.callback_query(F.data == "get_comment_form")
async def get_comment_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.comment)
    await try_edit_message(
        message=callback.message,
        text=hbold("Введите комментарий:"),
    )


@router.message(BidCreating.comment)
async def set_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.html_text)
    await clear_state_with_success(message, state)


# Documents
@router.callback_query(F.data == "get_document_form")
async def get_documents_form(callback: CallbackQuery, state: FSMContext):
    await handle_documents_form(callback.message, state, BidCreating.documents)


@router.message(BidCreating.documents)
async def set_documents(message: Message, state: FSMContext):
    async def clear_state_with_success_caller(message: Message, state: FSMContext):
        await clear_state_with_success(message, state, 0)

    await handle_documents(
        message,
        state,
        "document",
        clear_state_with_success_caller,
    )


# Need edm
@router.callback_query(F.data == "get_edm_form")
async def get_edm_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.edm)
    await callback.message.delete()
    await callback.message.answer(
        hbold("Счет в ЭДО?"), reply_markup=create_reply_keyboard("Да", "Нет")
    )


@router.message(BidCreating.edm)
async def set_edm(message: Message, state: FSMContext):
    if message.text == "⏪ Назад":
        await clear_state_with_success(message, state, sleep_time=0)
    elif message.text in ["Да", "Нет"]:
        await state.update_data(need_edm=message.text == "Да")
        await clear_state_with_success(message, state)
    else:
        await message.answer(format_err)


# Activity type
@router.callback_query(F.data == "get_activity_type_form")
async def get_activity_type_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.activity_type)
    await callback.message.delete()
    await callback.message.answer(
        hbold("Тип деятельности:"),
        reply_markup=create_reply_keyboard("Инвестиционная", "Текущая"),
    )


@router.message(BidCreating.activity_type)
async def set_activity_type(message: Message, state: FSMContext):
    if message.text == "⏪ Назад":
        await clear_state_with_success(message, state, sleep_time=0)
    elif message.text in ["Инвестиционная", "Текущая"]:
        await state.update_data(activity_type=message.text)
        await clear_state_with_success(message, state)
    else:
        await message.answer(format_err)


# History section


@router.callback_query(
    BidCallbackData.filter(F.type == BidViewType.creation),
    BidCallbackData.filter(F.endpoint_name == "create_documents"),
)
async def get_documents(
    callback: CallbackQuery, callback_data: BidCallbackData, state: FSMContext
):
    bid = get_bid_by_id(callback_data.id)
    media: list[InputMediaDocument] = []

    for document in bid.documents:
        media.append(
            InputMediaDocument(
                media=BufferedInputFile(
                    file=document.document.file.read(),
                    filename=document.document.filename,
                ),
            )
        )

    await try_delete_message(callback.message)
    msgs = await callback.message.answer_media_group(media=media)
    await state.update_data(msgs_for_delete=msgs)
    await msgs[0].reply(
        text=hbold("Выберите действие:"),
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text="Назад",
                callback_data=BidCallbackData(
                    id=bid.id,
                    mode=callback_data.mode,
                    type=BidViewType.creation,
                    endpoint_name="create_bid_info",
                ).pack(),
            )
        ),
    )


# Full info
@router.callback_query(
    BidCallbackData.filter(F.type == BidViewType.creation),
    BidCallbackData.filter(F.mode == BidViewMode.full),
    BidCallbackData.filter(F.endpoint_name == "create_bid_info"),
)
async def get_bid(
    message: CallbackQuery | Message, callback_data: BidCallbackData, state: FSMContext
):
    if isinstance(message, CallbackQuery):
        message = message.message
    bid_id = callback_data.id
    bid = get_bid_by_id(bid_id)
    data = await state.get_data()
    if "msgs_for_delete" in data:
        for msg in data["msgs_for_delete"]:
            await try_delete_message(msg)
        await state.update_data(msgs_for_delete=[])

    caption = get_full_bid_info(bid)

    await try_edit_message(
        message=message,
        text=caption,
        reply_markup=create_inline_keyboard(
            bid_create_history_button,
            InlineKeyboardButton(
                text="Показать документы",
                callback_data=BidCallbackData(
                    id=bid.id,
                    mode=callback_data.mode,
                    type=BidViewType.creation,
                    endpoint_name="create_documents",
                ).pack(),
            ),
        ),
    )


@router.callback_query(F.data == "get_create_history_bid")
async def get_bids_history(callback: CallbackQuery):
    bids = get_bids_by_worker_telegram_id(callback.message.chat.id)
    bids = sorted(bids, key=lambda bid: bid.create_date)[:10]
    keyboard = create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_bid_list_info(bid),
                callback_data=BidCallbackData(
                    id=bid.id,
                    mode=BidViewMode.full,
                    type=BidViewType.creation,
                    endpoint_name="create_bid_info",
                ).pack(),
            )
            for bid in bids
        ),
        create_bid_menu_button,
    )
    await try_delete_message(callback.message)
    await callback.message.answer("История заявок:", reply_markup=keyboard)


# Base info with state
@router.callback_query(
    BidCallbackData.filter(F.type == BidViewType.creation),
    BidCallbackData.filter(F.mode == BidViewMode.state_only),
    BidCallbackData.filter(F.endpoint_name == "create_bid_info"),
)
async def get_bid_state(callback: CallbackQuery, callback_data: BidCallbackData):
    bid_id = callback_data.id
    bid = get_bid_by_id(bid_id)
    await try_delete_message(callback.message)

    text = get_short_bid_info(bid)

    await callback.message.answer(
        text=text, reply_markup=create_inline_keyboard(bid_create_pending_button)
    )


@router.callback_query(F.data == "get_create_pending_bid")
async def get_bids_pending(callback: CallbackQuery):
    bids = get_pending_bids_by_worker_telegram_id(callback.message.chat.id)
    bids = sorted(bids, key=lambda bid: bid.create_date)[:10]
    keyboard = create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_bid_list_info(bid),
                callback_data=BidCallbackData(
                    id=bid.id,
                    mode=BidViewMode.state_only,
                    type=BidViewType.creation,
                    endpoint_name="create_bid_info",
                ).pack(),
            )
            for bid in bids
        ),
        create_bid_menu_button,
    )
    await try_delete_message(callback.message)
    await callback.message.answer("Ожидающие заявки:", reply_markup=keyboard)


# Search bid
@router.callback_query(F.data == bid_create_search_button.callback_data)
async def get_bid_id(message: CallbackQuery | Message, state: FSMContext):
    if isinstance(message, CallbackQuery):
        message = message.message
    await state.set_state(BidCreating.search)
    await try_delete_message(message)

    msg = await message.answer(
        text=hbold("Введите номер заявки:"),
        reply_markup=create_reply_keyboard(back),
    )
    await state.update_data(msg=msg)


@router.message(BidCreating.search)
async def find_bid(message: Message, state: FSMContext):
    from bot.handlers.bids.main import get_menu

    data = await state.get_data()
    await try_delete_message(data["msg"])
    await try_delete_message(message)

    await state.set_state(Base.none)

    if message.text == back:
        await get_menu(message, state)
    else:
        try:
            msg_text = int(message.text)
            bid = find_bid_for_worker(msg_text, message.chat.id)

            if bid is None:
                msg = await message.answer(text=hbold("Заявка не найдена!"))
                await asyncio.sleep(2)
                await get_bid_id(message, state)

            elif not bid:
                msg = await message.answer(
                    text=hbold("У Вас нет доступа к этой заявке!")
                )
                await asyncio.sleep(2)
                await get_bid_id(message, state)
            else:
                msg = await message.answer("Успешно!")
                await asyncio.sleep(1)

                await get_bid(
                    message,
                    BidCallbackData(
                        id=bid.id,
                        mode=BidViewMode.state_only,
                        type=BidViewType.creation,
                        endpoint_name="create_bid_info",
                    ),
                    state,
                )
        except ValueError:
            await try_delete_message(message)
            msg = await message.answer(hbold(format_err))

            await asyncio.sleep(2)
            await get_bid_id(message, state)
        finally:
            await msg.delete()
