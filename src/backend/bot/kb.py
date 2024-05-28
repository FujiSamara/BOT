from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext
from aiogram.types import Document

from db.schemas import WorkTimeSchema
from bot.handlers.rate.schemas import RateFormStatus, RateShiftCallbackData
from db.models import ApprovalStatus

# Buttons
main_menu_button = InlineKeyboardButton(text="Главное меню", callback_data="get_menu")

# Bid
settings_bid_menu_button = InlineKeyboardButton(
    text="Создать заявку", callback_data="get_bid_settings_menu"
)

create_bid_menu_button = InlineKeyboardButton(
    text="Согласование платежей", callback_data="get_create_bid_menu"
)


bid_create_history_button = InlineKeyboardButton(
    text="История заявок", callback_data="get_create_history_bid"
)
bid_create_pending_button = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_create_pending_bid"
)

kru_menu_button = InlineKeyboardButton(
    text="Согласование платежей", callback_data="get_kru_menu"
)
owner_menu_button = InlineKeyboardButton(
    text="Согласование платежей", callback_data="get_owner_menu"
)
accountant_card_menu_button = InlineKeyboardButton(
    text="Согласование платежей", callback_data="get_accountant_card_menu"
)
accountant_cash_menu_button = InlineKeyboardButton(
    text="Согласование платежей", callback_data="get_accountant_cash_menu"
)
teller_card_menu_button = InlineKeyboardButton(
    text="Согласование платежей", callback_data="get_teller_card_menu"
)
teller_cash_menu_button = InlineKeyboardButton(
    text="Согласование платежей", callback_data="get_teller_cash_menu"
)


# Keyboards
def create_inline_keyboard(
    *buttons: list[InlineKeyboardButton],
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])


def create_reply_keyboard(*texts: list[str]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=text)] for text in texts])


# Bid
bid_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [settings_bid_menu_button],
        [bid_create_pending_button],
        [bid_create_history_button],
        [main_menu_button],
    ]
)


async def get_create_bid_menu(state: FSMContext) -> InlineKeyboardMarkup:
    data = await state.get_data()
    amount = data.get("amount")
    payment_type = data.get("type")
    department = data.get("department")
    agreement = data.get("agreement")
    urgently = data.get("urgently")
    need_document = data.get("need_document")
    document1: Document = data.get("document1")
    document2: Document = data.get("document2")
    document3: Document = data.get("document3")
    document_text1 = "Отсутствует"
    document_text2 = "Отсутствует"
    document_text3 = "Отсутствует"

    all_field_exist = True

    if not amount:
        all_field_exist = False
        amount = "0"
    else:
        amount += " ✅"
    if not payment_type:
        all_field_exist = False
        payment_type = "Не указано"
    else:
        payment_type = payment_type_dict[payment_type] + " ✅"
    if not department:
        all_field_exist = False
        department = "Не указано"
    else:
        department += " ✅"
    if not agreement:
        agreement = "Нет ✅"
    else:
        agreement += " ✅"
    if not urgently:
        urgently = "Нет ✅"
    else:
        urgently += " ✅"
    if not need_document:
        need_document = "Нет ✅"
    else:
        need_document += " ✅"

    purpose_postfix = ""
    if "purpose" in data:
        purpose_postfix = " ✅"
    else:
        all_field_exist = False

    if not document1 and not document2 and not document3:
        all_field_exist = False
    if document1:
        if hasattr(document1, "file_name"):
            document_text1 = document1.file_name + " ✅"
        else:
            document_text1 = "Фотография" + " ✅"
    if document2:
        if hasattr(document2, "file_name"):
            document_text2 = document2.file_name + " ✅"
        else:
            document_text2 = "Фотография" + " ✅"
    if document3:
        if hasattr(document3, "file_name"):
            document_text3 = document3.file_name + " ✅"
        else:
            document_text3 = "Фотография" + " ✅"

    keyboard = [
        [
            InlineKeyboardButton(text="Сумма", callback_data="get_amount_form"),
            InlineKeyboardButton(text=amount, callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(text="Тип оплаты", callback_data="get_paymant_form"),
            InlineKeyboardButton(text=payment_type, callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="Предприятие", callback_data="get_department_form"
            ),
            InlineKeyboardButton(text=department, callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(text="Документ 1", callback_data="get_document_form1"),
            InlineKeyboardButton(text=document_text1, callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(text="Документ 2", callback_data="get_document_form2"),
            InlineKeyboardButton(text=document_text2, callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(text="Документ 3", callback_data="get_document_form3"),
            InlineKeyboardButton(text=document_text3, callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="Наличие договора", callback_data="get_agreement_form"
            ),
            InlineKeyboardButton(text=agreement, callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="Заявка срочная?", callback_data="get_urgently_form"
            ),
            InlineKeyboardButton(text=urgently, callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="Нужна платежка?", callback_data="get_need_document_form"
            ),
            InlineKeyboardButton(text=need_document, callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="Цель платежа" + purpose_postfix, callback_data="get_purpose_form"
            )
        ],
        [InlineKeyboardButton(text="Комментарий", callback_data="get_comment_form")],
        [create_bid_menu_button],
    ]
    if all_field_exist:
        keyboard.append(
            [InlineKeyboardButton(text="Отправить заявку", callback_data="send_bid")]
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


payment_type_dict = {
    "cash": "Наличная",
    "card": "Безналичная",
    "taxi": "Требуется такси",
}


approval_status_dict = {
    ApprovalStatus.approved: "Согласовано",
    ApprovalStatus.pending: "Ожидает поступления",
    ApprovalStatus.pending_approval: "Ожидает согласования",
    ApprovalStatus.denied: "Отклонено",
    ApprovalStatus.skipped: "Не требуется",
}

payment_type_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=payment_type_dict["cash"], callback_data="cash"),
            InlineKeyboardButton(text=payment_type_dict["card"], callback_data="card"),
        ],
        [InlineKeyboardButton(text=payment_type_dict["taxi"], callback_data="taxi")],
        [settings_bid_menu_button],
    ]
)


# Rating
rating_menu_button = InlineKeyboardButton(
    text="Меню оценки", callback_data="get_rating_menu"
)


def get_rating_worker_menu(
    fine: int, rating: int, record: WorkTimeSchema
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Оценка",
                    callback_data=RateShiftCallbackData(
                        day=record.day,
                        record_id=record.id,
                        rating=rating,
                        fine=fine,
                        form_status=RateFormStatus.RATING,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=str(rating),
                    callback_data="dummy",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Штраф",
                    callback_data=RateShiftCallbackData(
                        day=record.day,
                        record_id=record.id,
                        rating=rating,
                        fine=fine,
                        form_status=RateFormStatus.FINE,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=str(fine),
                    callback_data="dummy",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=RateShiftCallbackData(
                        day=record.day,
                        record_id=-1,
                        form_status=RateFormStatus.NONE,
                    ).pack(),
                )
            ],
        ]
    )


# Worker bid
worker_bid_menu_button = InlineKeyboardButton(
    text="Согласование кандидатов", callback_data="get_worker_bid_menu"
)

create_worker_bid_menu_button = InlineKeyboardButton(
    text="Согласовать кандидата", callback_data="get_create_worker_bid_menu"
)
worker_bid__history_button = InlineKeyboardButton(
    text="История согласования", callback_data="get_bid_settings_menu"
)


worker_bid_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [create_worker_bid_menu_button],
        [worker_bid__history_button],
        [main_menu_button],
    ]
)


async def get_create_worker_bid_menu(state: FSMContext) -> InlineKeyboardMarkup:
    data = await state.get_data()
    form_complete = True

    l_name = data.get("l_name")
    f_name = data.get("f_name")
    o_name = data.get("o_name")
    post = data.get("post")

    if not l_name:
        l_name = ""
        form_complete = False
    else:
        l_name += " ✅"

    if not f_name:
        f_name = ""
        form_complete = False
    else:
        f_name += " ✅"

    if not o_name:
        o_name = ""
        form_complete = False
    else:
        o_name += " ✅"

    if not post:
        post = ""
        form_complete = False
    else:
        post += " ✅"

    buttons = [
        [
            InlineKeyboardButton(text="Имя", callback_data="get_worker_bid_fname_form"),
            InlineKeyboardButton(
                text=str(f_name),
                callback_data="dummy",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Фамилия",
                callback_data="get_worker_bid_lname_form",
            ),
            InlineKeyboardButton(
                text=str(l_name),
                callback_data="dummy",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Отчество",
                callback_data="get_worker_bid_oname_form",
            ),
            InlineKeyboardButton(
                text=str(o_name),
                callback_data="dummy",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Должность",
                callback_data="get_worker_bid_post_form",
            ),
            InlineKeyboardButton(
                text=str(post),
                callback_data="dummy",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data="get_worker_bid_menu",
            )
        ],
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Отправить заявку", callback_data="send_worker_bid"
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
