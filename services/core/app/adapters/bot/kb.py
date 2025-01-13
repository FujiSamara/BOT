from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext

from app.schemas import WorkTimeSchema
from app.adapters.bot.handlers.rate.schemas import RateFormStatus, RateShiftCallbackData
from app.infra.database.models import ApprovalStatus, WorkerStatus

# Buttons
main_menu_button = InlineKeyboardButton(text="Главное меню", callback_data="get_menu")

# Bid
settings_bid_menu_button = InlineKeyboardButton(
    text="Создать заявку", callback_data="get_bid_settings_menu"
)

create_bid_menu_button = InlineKeyboardButton(
    text="Подать платёжную заявку", callback_data="get_create_bid_menu"
)


bid_create_history_button = InlineKeyboardButton(
    text="История заявок", callback_data="get_create_history_bid"
)
bid_create_pending_button = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_create_pending_bid"
)
bid_create_search_button = InlineKeyboardButton(
    text="Найти заявку", callback_data="get_create_search_bid"
)

fac_cc_menu_button = InlineKeyboardButton(
    text="Согласовать платёж ЦФО/ЦЗ", callback_data="get_fac_menu"
)
kru_menu_button = InlineKeyboardButton(
    text="Согласовать платёж КРУ", callback_data="get_kru_menu"
)
owner_menu_button = InlineKeyboardButton(
    text="Согласовать платёж учредитель", callback_data="get_owner_menu"
)
accountant_card_menu_button = InlineKeyboardButton(
    text="Согласовать платёж бухгалтерия", callback_data="get_accountant_card_menu"
)
accountant_cash_menu_button = InlineKeyboardButton(
    text="Согласовать платёж бухгалтерия", callback_data="get_accountant_cash_menu"
)
teller_card_menu_button = InlineKeyboardButton(
    text="Выплата денежных средств", callback_data="get_teller_card_menu"
)
teller_cash_menu_button = InlineKeyboardButton(
    text="Выдача денежных средств", callback_data="get_teller_cash_menu"
)


# Keyboards
def create_inline_keyboard(
    *buttons: list[InlineKeyboardButton],
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])


def create_reply_keyboard(*texts: list[str]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=text)] for text in texts])


def create_reply_keyboard_resize(*texts: list[str]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text)] for text in texts], resize_keyboard=True
    )


def create_reply_keyboard_raw(*texts: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [KeyboardButton(text=text) for text in texts]
    return ReplyKeyboardMarkup(keyboard=[keyboard], resize_keyboard=True)


# Bid
bid_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [settings_bid_menu_button],
        [bid_create_pending_button],
        [bid_create_history_button],
        [bid_create_search_button],
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
    need_edm = data.get("need_edm")
    activity_type = data.get("activity_type")

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

    activity_type_postfix = ""
    if not activity_type or len(activity_type) == 0:
        all_field_exist = False
    else:
        activity_type_postfix = " ✅"

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
            InlineKeyboardButton(text="Счет в ЭДО?", callback_data="get_edm_form"),
            InlineKeyboardButton(
                text="Да" if need_edm else "Нет", callback_data="dummy"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Цель платежа" + purpose_postfix, callback_data="get_purpose_form"
            )
        ],
        [
            InlineKeyboardButton(
                text="Тип деятельности" + activity_type_postfix,
                callback_data="get_activity_type_form",
            )
        ],
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
    ApprovalStatus.not_relevant: "Не релевантно",
}

approval_status_Technical_Request_dict = {
    ApprovalStatus.approved: "Выполнено",
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
    text="Подать заявку кандидата", callback_data="get_worker_bid_menu"
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


get_coordinate_worker_bids_AS_btn = InlineKeyboardButton(
    text="Согласование кандидатов бухгалтерия",
    callback_data="get_coordinate_worker_bids_AS",  # Accounting service
)

get_coordinate_worker_bids_SS_btn = InlineKeyboardButton(
    text="Согласование кандидатов СБ",
    callback_data="get_coordinate_worker_bids_SS",  # Security service
)

get_candidates_coordinate_menu_btn = InlineKeyboardButton(
    text="Сотрудники",
    callback_data="get_candidates_menu",
)

worker_status_dict = {
    WorkerStatus.pending_approval: "На согласовании",
    WorkerStatus.internship: "На стажировке",
    WorkerStatus.refusal_internship: "Отказ от стажировки",
    WorkerStatus.active: "В штате",
    WorkerStatus.process_dismissal: "В процессе увольнения",
    WorkerStatus.dismissal: "Уволен",
}


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
    birth_date = data.get("birth_date")
    phone_number = data.get("phone_number")

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

    if birth_date is None:
        birth_date = ""
        form_complete = False
    else:
        birth_date += " ✅"

    if phone_number is None:
        phone_number = ""
        form_complete = False
    else:
        phone_number += " ✅"

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
                text="Дата рождения",
                callback_data="get_worker_bid_birthdate_form",
            ),
            InlineKeyboardButton(
                text=birth_date,
                callback_data="dummy",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Номер телефона",
                callback_data="get_worker_bid_phone_number_form",
            ),
            InlineKeyboardButton(
                text=phone_number,
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


async def get_create_worker_bid_birthdate_menu(
    state: FSMContext,
) -> InlineKeyboardMarkup:
    data = await state.get_data()
    form_complete = True
    year = data.get("year")
    month = data.get("month")
    day = data.get("day")

    if year is None:
        year = ""
        form_complete = False
    else:
        year = str(year) + " ✅"

    if month is None:
        month = ""
        form_complete = False
    else:
        month = str(month) + " ✅"

    buttons = [
        [
            InlineKeyboardButton(
                text="Год",
                callback_data="get_worker_bid_birth_year",
            ),
            InlineKeyboardButton(
                text=year,
                callback_data="dummy",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Месяц",
                callback_data="get_worker_bid_birth_month",
            ),
            InlineKeyboardButton(
                text=month,
                callback_data="dummy",
            ),
        ],
    ]
    if form_complete:
        if day is None:
            day = ""
            form_complete = False
        else:
            day = str(day) + " ✅"
        buttons.append(
            [
                InlineKeyboardButton(
                    text="День",
                    callback_data="get_worker_bid_birth_day",
                ),
                InlineKeyboardButton(
                    text=day,
                    callback_data="dummy",
                ),
            ],
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data="get_create_worker_bid_menu",
            )
        ],
    )

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Дата верна", callback_data="set_worker_bid_birth_date"
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Bids IT

create_bid_it_menu_button = InlineKeyboardButton(
    text="Заявка в IT отдел", callback_data="get_create_bid_it_menu"
)

get_it_repairman_menu_btn = InlineKeyboardButton(
    text="IT заявки", callback_data="get_it_repairman_menu"
)

get_it_tm_menu_btn = InlineKeyboardButton(
    text="IT заявки ТУ", callback_data="get_it_tm_menu"
)


# region personal cabinet

get_personal_cabinet_button = InlineKeyboardButton(
    text="Личный кабинет",
    callback_data="get_per_cab",
)

get_per_cab_logins_button = InlineKeyboardButton(
    text="Доступы",
    callback_data="get_per_cab_logins",
)

get_per_cab_mat_vals_button = InlineKeyboardButton(
    text="Материальные ценности",
    callback_data="get_per_cab_mat_vals",
)

get_per_cab_dismissal_button = InlineKeyboardButton(  # issues 176
    text="Заявления",
    callback_data="get_per_cab_dismissal",
)

set_per_cab_department_button = InlineKeyboardButton(
    text="Смена предприятия",
    callback_data="set_per_cab_department",
)

get_menu_changing_form_button = InlineKeyboardButton(
    text="Сменить меню",
    callback_data="get_menu_changing_form_button",
)

get_per_cab_worktimes_button = InlineKeyboardButton(
    text="Смены", callback_data="get_per_cab_worktimes_button"
)
# endregion

# region monitoring
get_monitoring_menu_btn = InlineKeyboardButton(
    text="Мониторинг точек", callback_data="get_monitoring_menu"
)

get_monitoring_list_btn = InlineKeyboardButton(
    text="Статус оборудования",
    callback_data="get_monitoring_list",
)

get_incident_history_btn = InlineKeyboardButton(
    text="История инцидентов",
    callback_data="get_incident_history",
)

get_incidents_btn = InlineKeyboardButton(
    text="Инциденты",
    callback_data="get_incidents",
)

monitoring_menu = create_inline_keyboard(
    get_monitoring_list_btn,
    get_incident_history_btn,
    get_incidents_btn,
    main_menu_button,
)
# endregion
