from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext

from app.services import get_technical_problem_by_id, get_technical_request_by_id
from app.adapters.bot.handlers.tech_request.schemas import ShowRequestCallbackData
from app.adapters.bot.kb import main_menu_button

from app.database.schemas import TechnicalRequestSchema


# region Chief technician (CT)

ct_button = InlineKeyboardButton(text="Тех. заявки", callback_data="get_CT_TR")

ct_change_department_button = InlineKeyboardButton(
    text="Выбрать производство",
    callback_data="set_CT_TR_department",
)

ct_rm = InlineKeyboardMarkup(
    inline_keyboard=[
        [ct_change_department_button],
        [main_menu_button],
    ]
)

ct_own_button = InlineKeyboardButton(text="Мои заявки", callback_data="CT_TR_own")

ct_admin_button = InlineKeyboardButton(text="Все заявки", callback_data="CT_TR_admin")

ct_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [ct_own_button],
        [ct_admin_button],
        [ct_button],
    ]
)

ct_own_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="CT_TR_own_waiting"
)

ct_rework = InlineKeyboardButton(
    text="Заявки на доработку", callback_data="get_CT_TR_rework"
)

ct_own_history = InlineKeyboardButton(
    text="История заявок", callback_data="CT_TR_own_history"
)

ct_own_menu_button = InlineKeyboardButton(
    text="Назад", callback_data=ct_own_button.callback_data
)

ct_own_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [ct_own_waiting],
        [ct_rework],
        [ct_own_history],
        [ct_button],
    ]
)


async def _ct_repair_kb(
    state: FSMContext,
    callback_data: ShowRequestCallbackData,
    back_button: list[InlineKeyboardButton],
    photo_button: InlineKeyboardButton,
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
            photo_button,
            InlineKeyboardButton(text=f"{photo}", callback_data="dummy"),
        ],
        back_button,
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Отметить выполненной",
                    callback_data=ShowRequestCallbackData(
                        end_point="save_CT_TR_repair",
                        request_id=callback_data.request_id,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def ct_repair_waiting_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    back_button = [
        InlineKeyboardButton(
            text="К заявке",
            callback_data=ShowRequestCallbackData(
                request_id=callback_data.request_id,
                end_point="CT_TR_show_form_waiting",
                last_end_point=callback_data.last_end_point,
            ).pack(),
        )
    ]
    photo_button = InlineKeyboardButton(
        text="Фото после ремонта",
        callback_data=ShowRequestCallbackData(
            request_id=callback_data.request_id,
            end_point="get_CT_TR_photo_waiting",
            last_end_point=callback_data.last_end_point,
        ).pack(),
    )
    return await _ct_repair_kb(
        state=state,
        callback_data=callback_data,
        back_button=back_button,
        photo_button=photo_button,
    )


async def ct_repair_rework_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    back_button = [
        InlineKeyboardButton(
            text="К заявке",
            callback_data=ShowRequestCallbackData(
                request_id=callback_data.request_id,
                end_point="CT_TR_show_form_rework",
                last_end_point=callback_data.last_end_point,
            ).pack(),
        )
    ]
    photo_button = InlineKeyboardButton(
        text="Фото после ремонта",
        callback_data=ShowRequestCallbackData(
            request_id=callback_data.request_id,
            end_point="get_CT_TR_photo_rework",
            last_end_point=callback_data.last_end_point,
        ).pack(),
    )
    return await _ct_repair_kb(
        state=state,
        callback_data=callback_data,
        back_button=back_button,
        photo_button=photo_button,
    )


async def ct_admin_kb(
    state: FSMContext,
    callback_data: ShowRequestCallbackData,
) -> InlineKeyboardMarkup:
    data = await state.get_data()
    repairman = get_technical_request_by_id(callback_data.request_id).repairman
    repairman_full_name_old = " ".join(
        [repairman.l_name, repairman.f_name, repairman.o_name]
    )
    repairman_full_name_new = data.get("repairman_full_name")
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
                    end_point="get_CT_TR_executor_group",
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


async def ct_close_request_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    description = (await state.get_data()).get("description")
    form_complete = True
    if not description:
        description = ""
        form_complete = False
    else:
        if len(description) > 16:
            description = description[:16] + "..."
        description += " ✅"

    buttons = [
        [
            InlineKeyboardButton(
                text="Комментарий",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="CT_TR_close_request_description",
                ).pack(),
            ),
            InlineKeyboardButton(text=f"{description}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="Отмена",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="show_CT_TR_admin_form",
                ).pack(),
            ),
        ],
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Утвердить",
                    callback_data=ShowRequestCallbackData(
                        request_id=callback_data.request_id,
                        end_point="CT_TR_save_close_request",
                    ).pack(),
                ),
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# end region

# region Worker (WR)

wr_menu_button = InlineKeyboardButton(
    text="Тех. заявки", callback_data="get_WR_TR_menu"
)

wr_create = InlineKeyboardButton(text="Создать заявку", callback_data="get_TR_create")

wr_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_WR_TR_waiting"
)

wr_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_WR_TR_history"
)

wr_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [wr_create],
        [wr_waiting],
        [wr_history],
        [main_menu_button],
    ]
)


async def wr_create_kb(state: FSMContext) -> InlineKeyboardMarkup:
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
        [wr_menu_button],
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

rm_button = InlineKeyboardButton(text="Тех. заявки", callback_data="get_RM_TR")

rm_change_department_button = InlineKeyboardButton(
    text="Выбрать производство", callback_data="set_RM_TR_department"
)

rm_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_RM_TR_waiting"
)

rm_rework = InlineKeyboardButton(
    text="Заявки на доработку", callback_data="get_RM_TR_rework"
)

rm_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_RM_TR_history"
)

rm_change_department_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [rm_change_department_button],
        [main_menu_button],
    ]
)

rm_menu_button = InlineKeyboardButton(text="Назад", callback_data="get_RM_TR_menu")

rm_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [rm_waiting],
        [rm_rework],
        [rm_history],
        [rm_button],
    ]
)


async def rm_repair_kb(
    state: FSMContext,
    callback_data: ShowRequestCallbackData,
    back_button: list[InlineKeyboardButton],
    photo_button: InlineKeyboardButton,
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
            photo_button,
            InlineKeyboardButton(text=f"{photo}", callback_data="dummy"),
        ],
        back_button,
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Отметить выполненной",
                    callback_data=ShowRequestCallbackData(
                        end_point="save_RM_TR_repair",
                        request_id=callback_data.request_id,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def rm_repair_waiting_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    photo_button = InlineKeyboardButton(
        text="Фото после ремонта",
        callback_data=ShowRequestCallbackData(
            request_id=callback_data.request_id,
            end_point="get_RM_TR_waiting_photo",
            last_end_point=callback_data.last_end_point,
        ).pack(),
    )
    back_button = [
        InlineKeyboardButton(
            text="К заявке",
            callback_data=ShowRequestCallbackData(
                request_id=callback_data.request_id,
                end_point="RM_TR_show_form_waiting",
                last_end_point=callback_data.last_end_point,
            ).pack(),
        )
    ]
    return await rm_repair_kb(
        state=state,
        callback_data=callback_data,
        back_button=back_button,
        photo_button=photo_button,
    )


async def rm_repair_rework_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    photo_button = InlineKeyboardButton(
        text="Фото после ремонта",
        callback_data=ShowRequestCallbackData(
            request_id=callback_data.request_id,
            end_point="get_RM_TR_rework_photo",
            last_end_point=callback_data.last_end_point,
        ).pack(),
    )
    back_button = [
        InlineKeyboardButton(
            text="К заявке",
            callback_data=ShowRequestCallbackData(
                request_id=callback_data.request_id,
                end_point="RM_TR_show_form_rework",
                last_end_point=callback_data.last_end_point,
            ).pack(),
        )
    ]
    return await rm_repair_kb(
        state=state,
        callback_data=callback_data,
        back_button=back_button,
        photo_button=photo_button,
    )


# endregion

# region Territorial manager (TM)

tm_button = InlineKeyboardButton(text="Тех. заявки", callback_data="get_TM_TR")

tm_menu_button = InlineKeyboardButton(text="Назад", callback_data="get_TM_TR_menu")

tm_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_TM_TR_waiting"
)

tm_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_TM_TR_history"
)

tm_change_department_button = InlineKeyboardButton(
    text="Выбрать производство",
    callback_data="set_TM_TR_department",
)

tm_change_department_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [tm_change_department_button],
        [main_menu_button],
    ]
)

tm_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [tm_waiting],
        [tm_history],
        [tm_button],
    ]
)


async def tm_rate_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    data = await state.get_data()
    form_complete = True
    mark = data.get("mark")
    description = data.get("description")

    if not mark:
        mark_text = ""
        form_complete = False
    else:
        mark_text = f"{mark} ✅"
    if not description:
        description = ""
        form_complete = False
    else:
        description = (
            description if len(description) <= 16 else description[:16] + "..."
        )
        description += " ✅"

    buttons = [
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
        ],
        [
            InlineKeyboardButton(
                text="Комментарий",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="description_TM_TR",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            ),
            InlineKeyboardButton(text=f"{description}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="К заявке",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="TM_TR_show_form_waiting",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            )
        ],
    ]

    if form_complete:
        if mark > 1 or (
            get_technical_request_by_id(
                request_id=data.get("request_id")
            ).reopen_repair_date
            is not None
        ):
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

# region Department director

dd_button = InlineKeyboardButton(text="Тех. заявки", callback_data="get_DD_TR")

dd_menu_button = InlineKeyboardButton(text="Назад", callback_data="get_DD_TR_menu")

dd_active = InlineKeyboardButton(
    text="Активные заявки", callback_data="get_DD_TR_active"
)

dd_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_DD_TR_history"
)

dd_change_department_button = InlineKeyboardButton(
    text="Выбрать производство",
    callback_data="set_DD_TR_department",
)

dd_change_department_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [dd_change_department_button],
        [main_menu_button],
    ]
)

dd_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [dd_active],
        [dd_history],
        [dd_button],
    ]
)


async def dd_update_kb_executor(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    data = await state.get_data()
    form_complete = True

    repairman_full_name = data.get("repairman_full_name")
    repairman = get_technical_request_by_id(callback_data.request_id).repairman

    repairman_full_name_old = " ".join(
        [repairman.l_name, repairman.f_name, repairman.o_name]
    )

    if repairman_full_name and repairman_full_name != repairman_full_name_old:
        repairman_full_name = repairman_full_name.split(" ")[0] + "... ✅"
    else:
        repairman_full_name = repairman_full_name_old
        form_complete = False

    buttons = [
        [
            InlineKeyboardButton(
                text="Исполнитель",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="get_DD_TR_executor_group",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            ),
            InlineKeyboardButton(text=repairman_full_name, callback_data="dummy"),
        ],
    ]

    buttons.append(
        [
            InlineKeyboardButton(
                text="К заявке",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="DD_TR_show_form_active",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            )
        ]
    )

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Изменить",
                    callback_data=ShowRequestCallbackData(
                        request_id=callback_data.request_id,
                        end_point="DD_TR_save_change_executor",
                        last_end_point=callback_data.last_end_point,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def dd_update_problem_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    data = await state.get_data()
    form_complete = True
    problem_id = data.get("problem_id")
    problem_old = get_technical_request_by_id(
        request_id=callback_data.request_id
    ).problem

    if problem_id and problem_id != problem_old.id:
        problem_text = (get_technical_problem_by_id(problem_id).problem_name) + " ✅"

    else:
        problem_text = problem_old.problem_name
        form_complete = False

    buttons = [
        [
            InlineKeyboardButton(
                text="Проблема",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="get_DD_TR_problem",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            ),
            InlineKeyboardButton(text=problem_text, callback_data="dummy"),
        ],
    ]

    buttons.append(
        [
            InlineKeyboardButton(
                text="К заявке",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="DD_TR_show_form_active",
                    last_end_point=callback_data.last_end_point,
                ).pack(),
            )
        ]
    )

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Изменить",
                    callback_data=ShowRequestCallbackData(
                        request_id=callback_data.request_id,
                        end_point="DD_TR_save_change_problem",
                        last_end_point=callback_data.last_end_point,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def dd_close_request_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    description = (await state.get_data()).get("description")
    form_complete = True
    if not description:
        description = ""
        form_complete = False
    else:
        if len(description) > 16:
            description = description[:16] + "..."
        description += " ✅"

    buttons = [
        [
            InlineKeyboardButton(
                text="Комментарий",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="DD_TR_close_request_description",
                ).pack(),
            ),
            InlineKeyboardButton(text=f"{description}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="Отмена",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="DD_TR_show_form_active",
                ).pack(),
            ),
        ],
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Утвердить",
                    callback_data=ShowRequestCallbackData(
                        request_id=callback_data.request_id,
                        end_point="DD_TR_save_close_request",
                    ).pack(),
                ),
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
                        text=f"{request.department.name} {request.id} \
{request.reopen_deadline_date.strftime('%d.%m') if request.reopen_deadline_date else request.deadline_date.strftime('%d.%m')} до\
 {request.reopen_deadline_date.strftime('%H') if request.reopen_deadline_date else request.deadline_date.strftime('%H')}",
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
