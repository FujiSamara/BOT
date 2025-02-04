from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext

from app.adapters.bot.handlers.bids_it.schemas import BidITCallbackData, BidITViewMode
from app.adapters.bot.kb import (
    main_menu_button,
)

# Worker IT

settings_bid_it_menu_button = InlineKeyboardButton(
    text="Создать заявку", callback_data="get_bid_it_settings_menu"
)

bid_it_create_history_button = InlineKeyboardButton(
    text="История заявок", callback_data="get_create_history_bid_it"
)
bid_it_create_pending_button = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_create_pending_bid_it"
)

back_worker_button = InlineKeyboardButton(
    text="Назад", callback_data="get_create_bid_it_menu"
)

bid_it_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [settings_bid_it_menu_button],
        [bid_it_create_pending_button],
        [bid_it_create_history_button],
        [main_menu_button],
    ]
)


async def get_create_bid_it_menu(state: FSMContext) -> InlineKeyboardMarkup:
    data = await state.get_data()
    problem = data.get("problem")
    document = data.get("photo")
    photo_text = "Отсутствует"
    comment = data.get("comment")
    all_field_exist = True

    if not problem:
        all_field_exist = False
        problem = "Не указано"
    else:
        problem = "✅ " + problem

    if not comment:
        all_field_exist = False
        comment = "Не указано"
    else:
        comment = "✅ " + comment

    if not document or len(document) == 0:
        all_field_exist = False
        photo_text = "0"
    else:
        photo_text = f"✅ {len(document)}"

    keyboard = [
        [
            InlineKeyboardButton(text="Проблема", callback_data="get_problem_it"),
            InlineKeyboardButton(text=problem, callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(text="Опишите проблему", callback_data="get_comment"),
            InlineKeyboardButton(text=comment, callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(text="Фото", callback_data="get_photo"),
            InlineKeyboardButton(text=photo_text, callback_data="dummy"),
        ],
    ]
    if all_field_exist:
        keyboard.append(
            [InlineKeyboardButton(text="Отправить заявку", callback_data="send_bid_it")]
        )
    keyboard.append([back_worker_button])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Repairman IT

get_it_repairman_menu_bts = InlineKeyboardButton(
    text="Выбрать предприятие", callback_data="get_it_repairman_menu"
)

get_department_it_repairman = InlineKeyboardButton(
    text="Выбрать предприятие", callback_data="get_department_it_repairman"
)

bids_pending_for_repairman = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="bids_pending_for_repairman"
)

bid_it_rm_create_history_button = InlineKeyboardButton(
    text="История заявок", callback_data="get_create_history_bid_it_rm"
)

bids_it_denied_for_repairman = InlineKeyboardButton(
    text="Отклоненные заявки", callback_data="bids_it_denied_for_repairman"
)

back_repairman_button = InlineKeyboardButton(text="Назад", callback_data="get_back_rm")

repairman_department_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [get_department_it_repairman],
        [main_menu_button],
    ]
)


repairman_bids_it_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [bids_pending_for_repairman],
        [bids_it_denied_for_repairman],
        [bid_it_rm_create_history_button],
        [get_it_repairman_menu_bts],
    ]
)


async def get_create_repairman_it_menu(
    callback_data: BidITCallbackData, state: FSMContext
) -> InlineKeyboardMarkup:
    data = await state.get_data()
    photo = ""
    photo_callback_data = ""
    if callback_data.mode == BidITViewMode.pending:
        photo = data.get("photo_work")
        photo_callback_data = "get_photo_work_rm"
    elif callback_data.mode == BidITViewMode.deny:
        photo = data.get("photo_rework")
        photo_callback_data = "get_photo_rework_rm"
    photo_text = "Отсутствует"
    all_field_exist = True

    if not photo or len(photo) == 0:
        all_field_exist = False
        photo_text = "0"
    else:
        photo_text = f"✅ {len(photo)}"

    keyboard = [
        [
            InlineKeyboardButton(text="Фото", callback_data=photo_callback_data),
            InlineKeyboardButton(text=photo_text, callback_data="dummy"),
        ],
    ]
    if all_field_exist:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Выполнить заявку",
                    callback_data=BidITCallbackData(
                        id=callback_data.id,
                        mode=callback_data.mode,
                        endpoint_name="send_bid_it_rm",
                    ).pack(),
                )
            ]
        )
    keyboard.append(
        [InlineKeyboardButton(text="Назад", callback_data=callback_data.pack())]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


take_bid_it_for_repairman = InlineKeyboardButton(
    text="Выполнить заявку", callback_data="take_bid_it_for_repairman"
)

take_bid_it_for_repairman_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [take_bid_it_for_repairman],
        [bids_pending_for_repairman],
    ]
)


# Territorial manager IT

get_it_tm_menu_bts = InlineKeyboardButton(
    text="Выбрать предприятие", callback_data="get_it_tm_menu"
)

bids_pending_for_tm = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="bids_pending_for_tm"
)

bid_it_tm_create_history_button = InlineKeyboardButton(
    text="История заявок", callback_data="get_create_history_bid_it_tm"
)

get_department_it_tm = InlineKeyboardButton(
    text="Выбрать предприятие", callback_data="get_department_it_tm"
)

back_tm_button = InlineKeyboardButton(text="Назад", callback_data="get_back_tm")


tm_department_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [get_department_it_tm],
        [main_menu_button],
    ]
)

tm_bids_it_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [bids_pending_for_tm],
        [bid_it_tm_create_history_button],
        [get_it_tm_menu_bts],
    ]
)


async def get_create_tm_bid_it_menu(
    callback_data: BidITCallbackData, state: FSMContext
) -> InlineKeyboardMarkup:
    data = await state.get_data()
    mark: int | None = data.get("mark")
    mark_text = "Отсутствует"
    work_comment: str | None = data.get("work_comment")
    work_comment_text = "Отсутствует"
    all_field_exist = True
    is_bad_work = False

    if mark is None:
        all_field_exist = False
    elif mark in range(1, 3):
        is_bad_work = True
        mark_text = f"✅ {mark}"
    elif mark in range(3, 6):
        mark_text = f"✅ {mark}"
    else:
        all_field_exist = False

    if mark is not None and is_bad_work:
        if work_comment is None:
            all_field_exist = False
        else:
            work_comment_text = f"✅ {work_comment}"

    keyboard = [
        [
            InlineKeyboardButton(text="Оценка работы", callback_data="get_mark_tm"),
            InlineKeyboardButton(text=mark_text, callback_data="dummy"),
        ],
    ]
    if is_bad_work:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Комментарий", callback_data="get_work_comment_tm"
                ),
                InlineKeyboardButton(text=work_comment_text, callback_data="dummy"),
            ]
        )
    if all_field_exist:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Утвердить заявку", callback_data="send_bid_it_tm"
                )
            ]
        )
    keyboard.append(
        [InlineKeyboardButton(text="Назад", callback_data=callback_data.pack())]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
