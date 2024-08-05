from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext

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
    document = data.get("document")
    expenditure = data.get("expenditure")

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
    if not expenditure:
        all_field_exist = False
        expenditure = "Не указано"
    else:
        expenditure += " ✅"

    purpose_postfix = ""
    if "purpose" in data:
        purpose_postfix = " ✅"
    else:
        all_field_exist = False

    if not document or len(document) == 0:
        all_field_exist = False
        document = "0"
    else:
        document = f"{len(document)} ✅"

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
            InlineKeyboardButton(
                text="Статья", callback_data="get_expenditure_chapter_form"
            ),
            InlineKeyboardButton(text=expenditure, callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(text="Документы", callback_data="get_document_form"),
            InlineKeyboardButton(text=document, callback_data="dummy"),
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
worker_bid_history_button = InlineKeyboardButton(
    text="История согласования", callback_data="get_worker_bid_history"
)


worker_bid_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [create_worker_bid_menu_button],
        [worker_bid_history_button],
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
    department = data.get("department")
    worksheet = data.get("worksheet")
    passport = data.get("passport")
    work_permission = data.get("work_permission")

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

    if not department:
        department = ""
        form_complete = False
    else:
        department += " ✅"

    if not worksheet or len(worksheet) == 0:
        worksheet = ""
        form_complete = False
    else:
        worksheet = f"{len(worksheet)} ✅"

    if not passport or len(passport) == 0:
        passport = ""
        form_complete = False
    else:
        passport = f"{len(passport)} ✅"

    if not work_permission or len(work_permission) == 0:
        work_permission = ""
    else:
        work_permission = f"{len(work_permission)}"

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
                text="Предприятие",
                callback_data="get_worker_bid_department_form",
            ),
            InlineKeyboardButton(
                text=str(department),
                callback_data="dummy",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Анкета",
                callback_data="get_worker_bid_worksheet_form",
            ),
            InlineKeyboardButton(
                text=str(worksheet),
                callback_data="dummy",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Паспорт",
                callback_data="get_worker_bid_passport_form",
            ),
            InlineKeyboardButton(
                text=str(passport),
                callback_data="dummy",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Разрешение на работу",
                callback_data="get_worker_bid_work_permission_form",
            ),
            InlineKeyboardButton(
                text=str(work_permission),
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


# Techical request
tech_req_menu_button = InlineKeyboardButton(
    text="Тех. заявки", callback_data="get_tech_req_menu"
)


tech_req_create = InlineKeyboardButton(
    text="Создать заявку", callback_data="get_tech_req_create"
)

tech_req_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_tech_req_waiting"
)

tech_req_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_tech_req_history"
)

tech_req_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [tech_req_create],
        [tech_req_waiting],
        [tech_req_history],
        [main_menu_button],
    ]
)


tech_problem = InlineKeyboardButton(
    text="Создать проблему", callback_data="create_tech_problem"
)


async def create_tech_req_kb(state: FSMContext) -> InlineKeyboardMarkup:
    data = await state.get_data()
    form_complete = True
    problem_name = data.get("problem_name")
    description = data.get("description")
    photo = data.get("photo")

    if not problem_name:
        problem_name = ""
        form_complete = False
    else:
        if len(problem_name) > 16:
            problem_name = problem_name[:16] + "..."
        problem_name += " ✅"

    if not description:
        description = ""
        form_complete = False
    else:
        if len(description) > 16:
            description = description[:16] + "..."
        description += " ✅"

    if not photo or len(photo) == 0:
        photo = ""
        form_complete = False
    else:
        photo = f"{len(photo)}"

    buttons = [
        [
            InlineKeyboardButton(
                text="Проблема", callback_data="problem_type_tech_req"
            ),
            InlineKeyboardButton(text=f"{problem_name}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="Комментарий", callback_data="description_tech_req"
            ),
            InlineKeyboardButton(text=f"{description}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(text="Фото", callback_data="photo_tech_req"),
            InlineKeyboardButton(text=f"{photo}", callback_data="dummy"),
        ],
        [tech_req_menu_button],
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Отправить проблему", callback_data="send_tech_req"
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_tech_problem_kb(state: FSMContext) -> InlineKeyboardMarkup:
    data = await state.get_data()
    form_complete = True
    problem_name = data.get("problem_name")

    buttons = [
        [
            InlineKeyboardButton(text="Имя", callback_data="get_problem_name"),
            InlineKeyboardButton(
                text=str(problem_name),
                callback_data="dummy",
            ),
        ]
    ]

    if not problem_name:
        problem_name = ""
        form_complete = False
    else:
        problem_name += " ✅"

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Отправить проблему", callback_data="send_tech_problem"
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


tech_req_status_dict = {}
