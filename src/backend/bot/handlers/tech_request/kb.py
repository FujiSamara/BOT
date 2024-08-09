from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext

from bot.handlers.tech_request.schemas import ShowRequestCallbackData
from bot.kb import main_menu_button

from db.schemas import TechnicalRequestSchema

# region Chief tecnician
CT_button = InlineKeyboardButton(
    text="Тех. заявки", callback_data="get_chief_technician_tech_req"
)

CT_change_department_button = InlineKeyboardButton(
    text="Выбрать производство",
    callback_data="set_chief_technician_tech_req_department",
)

CT_rm = InlineKeyboardMarkup(
    inline_keyboard=[
        [CT_change_department_button],
        [main_menu_button],
    ]
)

CT_own_button = InlineKeyboardButton(
    text="Мои заявки", callback_data="chief_technician_tech_req_own"
)

CT_admin_button = InlineKeyboardButton(
    text="Все заявки", callback_data="chief_technician_tech_req_admin"
)

CT_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [CT_own_button],
        [CT_admin_button],
        [CT_button],
    ]
)

CT_own_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="chief_technician_tech_req_own_waiting"
)

CT_own_history = InlineKeyboardButton(
    text="История заявок", callback_data="chief_technician_tech_req_own_history"
)

CT_own_menu_button = InlineKeyboardButton(
    text="Назад", callback_data=CT_own_button.callback_data
)

CT_own_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [CT_own_waiting],
        [CT_own_history],
        [CT_button],
    ]
)


async def CT_repair_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    data = await state.get_data()
    form_complete = True
    photo = data.get("photo")

    if not photo or len(photo) == 0:
        photo = ""
        form_complete = False
    else:
        photo = f"{len(photo)} ✅"
    buttons = [
        [
            InlineKeyboardButton(
                text="Фото после ремонта",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="get_CT_photo",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            ),
            InlineKeyboardButton(text=f"{photo}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="К заявке",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="chief_technician_show_form_waiting",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            )
        ],
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Отметить выполненой",
                    callback_data=ShowRequestCallbackData(
                        end_point="save_chief_technician_repair",
                        request_id=callback_data.request_id,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# end region

# region Worker

WR_menu_button = InlineKeyboardButton(
    text="Тех. заявки", callback_data="get_worker_tech_req_menu"
)

WR_create = InlineKeyboardButton(
    text="Создать заявку", callback_data="get_tech_req_create"
)

WR_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_worker_tech_req_waiting"
)

WR_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_worker_tech_req_history"
)

WR_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [WR_create],
        [WR_waiting],
        [WR_history],
        [main_menu_button],
    ]
)


async def WR_create_kb(state: FSMContext) -> InlineKeyboardMarkup:
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
            InlineKeyboardButton(text="Поломка", callback_data="problem_type_tech_req"),
            InlineKeyboardButton(text=f"{problem_name}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="Комментарий", callback_data="description_tech_req"
            ),
            InlineKeyboardButton(text=f"{description}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(text="Фото поломки", callback_data="photo_tech_req"),
            InlineKeyboardButton(text=f"{photo}", callback_data="dummy"),
        ],
        [WR_menu_button],
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Отправить проблему", callback_data="send_worker_tech_req"
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# endregion

# region Repairman

RM_button = InlineKeyboardButton(
    text="Тех. заявки", callback_data="get_repairman_tech_req"
)

RM_change_department_button = InlineKeyboardButton(
    text="Выбрать производство", callback_data="set_repairman_tech_req_department"
)

RM_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_repairman_tech_req_waiting"
)

RM_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_repairman_tech_req_history"
)

RM_change_deparment_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [RM_change_department_button],
        [main_menu_button],
    ]
)

RM_menu_button = InlineKeyboardButton(
    text="Назад", callback_data="get_repairman_tech_req_menu"
)

RM_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [RM_waiting],
        [RM_history],
        [RM_button],
    ]
)


async def RM_repair_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    data = await state.get_data()
    form_complete = True
    photo = data.get("photo")

    if not photo or len(photo) == 0:
        photo = ""
        form_complete = False
    else:
        photo = f"{len(photo)} ✅"
    buttons = [
        [
            InlineKeyboardButton(
                text="Фото после ремонта",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="get_repairman_photo",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            ),
            InlineKeyboardButton(text=f"{photo}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="К заявке",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="repairman_show_form_waiting",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            )
        ],
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Отметить выполненой",
                    callback_data=ShowRequestCallbackData(
                        end_point="save_repairman_repair",
                        request_id=callback_data.request_id,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# endregion

# region Territorial manager

TM_button = InlineKeyboardButton(
    text="Тех. заявки", callback_data="get_territorial_manager_tech_req"
)

TM_menu_button = InlineKeyboardButton(
    text="Назад", callback_data="get_territorial_manager_tech_req_menu"
)

TM_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_territorial_manager_tech_req_waiting"
)

TM_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_territorial_manager_tech_req_history"
)

TM_change_department_button = InlineKeyboardButton(
    text="Выбрать производство",
    callback_data="set_territorial_manager_tech_req_department",
)

TM_change_deparment_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [TM_change_department_button],
        [main_menu_button],
    ]
)

TM_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [TM_waiting],
        [TM_history],
        [TM_button],
    ]
)


async def TM_rate_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    data = await state.get_data()
    form_complete = True
    mark = data.get("mark")

    if not mark:
        mark_text = ""
        form_complete = False
    else:
        mark_text = f"{mark} ✅"
    buttons = [
        [
            InlineKeyboardButton(
                text="Оценка",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="territorial_manager_rate_tech_request",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            ),
            InlineKeyboardButton(text=f"{mark_text}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="К заявке",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="territorial_manager_show_form_waiting",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            )
        ],
    ]

    if form_complete:
        if mark >= 3:
            text = "Закрыть заявку"
        else:
            text = "Отправить на доработку"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=ShowRequestCallbackData(
                        end_point="save_tech_req_territorial_manager_rate",
                        request_id=callback_data.request_id,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# endregion

# region Universal


def create_kb_with_end_point(
    requests: list[TechnicalRequestSchema],
    end_point: str,
    menu_button: InlineKeyboardButton,
) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    try:
        for request in requests:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{request.department.name} {request.id}",
                        callback_data=ShowRequestCallbackData(
                            request_id=request.id, end_point=end_point
                        ).pack(),
                    )
                ]
            )
    finally:
        buttons.append([menu_button])
        return InlineKeyboardMarkup(inline_keyboard=buttons)


# endregion
