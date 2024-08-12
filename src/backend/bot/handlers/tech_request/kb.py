from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext

from bot.handlers.tech_request.schemas import ShowRequestCallbackData
from bot.kb import main_menu_button

from db.schemas import TechnicalRequestSchema


# region Chief tecnician (CT)

CT_button = InlineKeyboardButton(text="Тех. заявки", callback_data="get_CT_TR")

CT_change_department_button = InlineKeyboardButton(
    text="Выбрать производство",
    callback_data="set_CT_TR_department",
)

CT_rm = InlineKeyboardMarkup(
    inline_keyboard=[
        [CT_change_department_button],
        [main_menu_button],
    ]
)

CT_own_button = InlineKeyboardButton(text="Мои заявки", callback_data="CT_TR_own")

CT_admin_button = InlineKeyboardButton(text="Все заявки", callback_data="CT_TR_admin")

CT_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [CT_own_button],
        [CT_admin_button],
        [CT_button],
    ]
)

CT_own_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="CT_TR_own_waiting"
)

CT_own_history = InlineKeyboardButton(
    text="История заявок", callback_data="CTn_TR_own_history"
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
                    end_point="get_CT_TR_photo",
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
                    end_point="CT_TR_show_form_waiting",
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
                        end_point="save_CT_TR_repair",
                        request_id=callback_data.request_id,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def CT_admin_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    data = await state.get_data()
    repairman_full_name_old = data.get("repairman_full_name_old")
    repairman_full_name_new = data.get("repairman_full_name_new")
    form_complete = True

    if repairman_full_name_new and repairman_full_name_new != repairman_full_name_old:
        repairman_full_name = repairman_full_name_new + " ✅"
        form_complete = True
    else:
        repairman_full_name = repairman_full_name_old
        form_complete = False
    buttons = [
        [
            InlineKeyboardButton(
                text="Ответственный",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="get_CT_TR_executor",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            ),
            InlineKeyboardButton(text=f"{repairman_full_name}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="К заявке",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="show_CT_TR_admin_form",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            )
        ],
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Утвердить",
                    callback_data=ShowRequestCallbackData(
                        end_point="save_CT_TR_admin_form",
                        request_id=callback_data.request_id,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# end region

# region Worker (WR)

WR_menu_button = InlineKeyboardButton(
    text="Тех. заявки", callback_data="get_WR_TR_menu"
)

WR_create = InlineKeyboardButton(text="Создать заявку", callback_data="get_TR_create")

WR_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_WR_TR_waiting"
)

WR_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_WR_TR_history"
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
            InlineKeyboardButton(text="Поломка", callback_data="problem_type_WR_TR"),
            InlineKeyboardButton(text=f"{problem_name}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(text="Комментарий", callback_data="description_WR_TR"),
            InlineKeyboardButton(text=f"{description}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(text="Фото поломки", callback_data="photo_WR_TR"),
            InlineKeyboardButton(text=f"{photo}", callback_data="dummy"),
        ],
        [WR_menu_button],
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Отправить проблему", callback_data="send_WR_TR"
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# endregion

# region Repairman (RM)

RM_button = InlineKeyboardButton(text="Тех. заявки", callback_data="get_RM_TR")

RM_change_department_button = InlineKeyboardButton(
    text="Выбрать производство", callback_data="set_RM_TR_department"
)

RM_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_RM_TR_waiting"
)

RM_rework = InlineKeyboardButton(
    text="Заявки на доработку", callback_data="get_RM_TR_rework"
)

RM_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_RM_TR_history"
)

RM_change_deparment_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [RM_change_department_button],
        [main_menu_button],
    ]
)

RM_menu_button = InlineKeyboardButton(text="Назад", callback_data="get_RM_TR_menu")

RM_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [RM_waiting],
        [RM_rework],
        [RM_history],
        [RM_button],
    ]
)


async def RM_repair_kb(
    state: FSMContext,
    callback_data: ShowRequestCallbackData,
    request_button: list[InlineKeyboardButton],
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
                    end_point="get_RM_TR_photo",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            ),
            InlineKeyboardButton(text=f"{photo}", callback_data="dummy"),
        ],
        request_button,
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Отметить выполненой",
                    callback_data=ShowRequestCallbackData(
                        end_point="save_RM_TR_repair",
                        request_id=callback_data.request_id,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def RM_repair_waiting_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    request_button = [
        InlineKeyboardButton(
            text="К заявке",
            callback_data=ShowRequestCallbackData(
                request_id=callback_data.request_id,
                end_point="RM_TR_show_form_waiting",
                last_end_point=callback_data.last_end_point,
            ).pack(),
        )
    ]
    return await RM_repair_kb(
        state=state, callback_data=callback_data, request_button=request_button
    )


async def RM_repair_rework_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    request_button = [
        InlineKeyboardButton(
            text="К заявке",
            callback_data=ShowRequestCallbackData(
                request_id=callback_data.request_id,
                end_point="RM_TR_show_form_rework",
                last_end_point=callback_data.last_end_point,
            ).pack(),
        )
    ]
    return await RM_repair_kb(
        state=state, callback_data=callback_data, request_button=request_button
    )


# endregion

# region Territorial manager (TM)

TM_button = InlineKeyboardButton(text="Тех. заявки", callback_data="get_TM_TR")

TM_menu_button = InlineKeyboardButton(text="Назад", callback_data="get_TM_TR_menu")

TM_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_TM_TR_waiting"
)

TM_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_TM_TR_history"
)

TM_change_department_button = InlineKeyboardButton(
    text="Выбрать производство",
    callback_data="set_TM_TR_department",
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
    description = data.get("description")
    buttons = []
    desc_button = None

    if not mark:
        mark_text = ""
        form_complete = False
    else:
        mark_text = f"{mark} ✅"
        if mark < 3:
            if not description:
                description = ""
                form_complete = False
            else:
                description = (
                    description if len(description) <= 16 else description[:16] + "..."
                )
                description += " ✅"

            desc_button = [
                InlineKeyboardButton(
                    text="Комментарий",
                    callback_data=ShowRequestCallbackData(
                        request_id=callback_data.request_id,
                        end_point="description_TM_TR",
                        last_end_point=callback_data.last_end_point,
                    ).pack(),
                ),
                InlineKeyboardButton(text=f"{description}", callback_data="dummy"),
            ]

    buttons.append(
        [
            InlineKeyboardButton(
                text="Оценка",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="TM_TR_rate",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            ),
            InlineKeyboardButton(text=f"{mark_text}", callback_data="dummy"),
        ]
    )
    if desc_button:
        buttons.append(desc_button)
    buttons.append(
        [
            InlineKeyboardButton(
                text="К заявке",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="TM_TR_show_form_waiting",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            )
        ]
    )

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
                        end_point="save_TM_TR_rate",
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
                        text=f"{request.id} {request.deadline_date.strftime("%d.%m")} до {request.deadline_date.strftime("%H")}",
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
