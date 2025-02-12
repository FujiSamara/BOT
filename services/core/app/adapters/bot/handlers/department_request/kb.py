from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext

from app.services import get_technical_problem_by_id, get_technical_request_by_id
from app.adapters.bot.handlers.department_request.schemas import (
    ShowRequestCallbackData,
    RequestType,
)
from app.adapters.bot.kb import main_menu_button
from app.adapters.bot.text import back

from app.schemas import TechnicalRequestSchema, CleaningRequestSchema


# region Chief technician (CT)

ct_button = InlineKeyboardButton(
    text="Технические заявки главный техник", callback_data="get_CT_TR"
)

ct_change_department_button = InlineKeyboardButton(
    text="Выбрать предприятие",
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
    text=back, callback_data=ct_own_button.callback_data
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
        text="Фото проделанной работы",
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
        text="Фото проделанной работы",
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
    text="Проблемы на предприятие", callback_data="get_WR_TR_CR_menu"
)

wr_create = InlineKeyboardButton(
    text="Создать заявку", callback_data="get_WR_TR_CR_create"
)

wr_waiting = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_WR_TR_CR_waiting"
)

wr_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_WR_TR_CR_history"
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
    from app.adapters.bot.text import back

    data = await state.get_data()
    form_complete = True
    problem_name = data.get("problem_name")
    description = data.get("description")
    photo = data.get("photo")
    department_name = data.get("dep_name")

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

    if not department_name:
        department_name = ""
        form_complete = False
    else:
        department_name += " ✅"

    buttons = [
        [
            InlineKeyboardButton(
                text="Проблема",
                callback_data="problem_group_WR_TR_CR",
            ),
            InlineKeyboardButton(text=f"{problem_name}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="Комментарий", callback_data="description_WR_TR_CR"
            ),
            InlineKeyboardButton(text=f"{description}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="Предприятие", callback_data="department_WR_TR_CR"
            ),
            InlineKeyboardButton(text=f"{department_name}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(text="Фото проблемы", callback_data="photo_WR_TR_CR"),
            InlineKeyboardButton(text=f"{photo}", callback_data="dummy"),
        ],
        [InlineKeyboardButton(text=back, callback_data=wr_menu_button.callback_data)],
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Отправить проблему", callback_data="send_WR_TR_CR"
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# endregion

# region Executors (Repairman and Cleaner)

repairman_button = InlineKeyboardButton(
    text="Технические заявки техник", callback_data="get_RM_TR"
)


cleaner_button = InlineKeyboardButton(
    text="Заявки клининг клинер", callback_data="get_Cleaner_CR"
)


async def executer_repair_kb(
    state: FSMContext,
    callback_data: ShowRequestCallbackData,
    back_button: list[InlineKeyboardButton],
    photo_button: InlineKeyboardButton,
    executor_type: RequestType,
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
                        end_point=f"save_{executor_type.name}_work",
                        request_id=callback_data.request_id,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def executer_work_waiting_kb(
    state: FSMContext,
    callback_data: ShowRequestCallbackData,
    executor_type: RequestType,
) -> InlineKeyboardMarkup:
    photo_button = InlineKeyboardButton(
        text="Фото проделанной работы",
        callback_data=ShowRequestCallbackData(
            request_id=callback_data.request_id,
            end_point=f"get_{executor_type.name}_waiting_photo",
            last_end_point=callback_data.last_end_point,
        ).pack(),
    )
    back_button = [
        InlineKeyboardButton(
            text="К заявке",
            callback_data=ShowRequestCallbackData(
                request_id=callback_data.request_id,
                end_point=f"{executor_type.name}_show_waiting_form",
                last_end_point=callback_data.last_end_point,
            ).pack(),
        )
    ]
    return await executer_repair_kb(
        state=state,
        callback_data=callback_data,
        back_button=back_button,
        photo_button=photo_button,
        executor_type=executor_type,
    )


async def executor_repair_rework_kb(
    state: FSMContext,
    callback_data: ShowRequestCallbackData,
    executor_type: RequestType,
) -> InlineKeyboardMarkup:
    photo_button = InlineKeyboardButton(
        text="Фото проделанной работы",
        callback_data=ShowRequestCallbackData(
            request_id=callback_data.request_id,
            end_point=f"get_{executor_type.name}_rework_photo",
            last_end_point=callback_data.last_end_point,
        ).pack(),
    )
    back_button = [
        InlineKeyboardButton(
            text="К заявке",
            callback_data=ShowRequestCallbackData(
                request_id=callback_data.request_id,
                end_point=f"{executor_type.name}_show_rework_form",
                last_end_point=callback_data.last_end_point,
            ).pack(),
        )
    ]
    return await executer_repair_kb(
        state=state,
        callback_data=callback_data,
        back_button=back_button,
        photo_button=photo_button,
        executor_type=executor_type,
    )


# endregion

# region Appraiser (AR)

AR_TR_button = InlineKeyboardButton(
    text="Приём технических заявок", callback_data="get_AR_TR"
)

AR_CR_button = InlineKeyboardButton(
    text="Приём заявок клининга", callback_data="get_AR_CR"
)


async def ar_rate_kb(
    state: FSMContext,
    callback_data: ShowRequestCallbackData,
    problem_type: RequestType,
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
                    end_point=f"{problem_type.name}_rate_AR",
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
                    end_point=f"{problem_type.name}_description_AR",
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
                    end_point=f"{problem_type.name}_show_waiting_form_AR",
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
                        end_point=f"{problem_type.name}_save_rate_AR",
                        request_id=callback_data.request_id,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# endregion

# region Extensive director

ed_button = InlineKeyboardButton(
    text="Технические заявки директор", callback_data="get_ED_TR"
)

ed_menu_button = InlineKeyboardButton(text="Назад", callback_data="get_ED_TR_menu")

ed_active = InlineKeyboardButton(
    text="Активные заявки", callback_data="get_ED_TR_active"
)

ed_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_ED_TR_history"
)

ed_change_department_button = InlineKeyboardButton(
    text="Выбрать предприятие",
    callback_data="set_ED_TR_department",
)

ed_change_department_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [ed_change_department_button],
        [main_menu_button],
    ]
)

ed_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [ed_active],
        [ed_history],
        [ed_button],
    ]
)


async def ed_update_kb_executor(
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
                    end_point="get_ED_TR_executor_group",
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
                    end_point="ED_TR_show_form_active",
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
                        end_point="ED_TR_save_change_executor",
                        last_end_point=callback_data.last_end_point,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def ed_update_problem_kb(
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
                    end_point="get_ED_TR_problem",
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
                    end_point="ED_TR_show_form_active",
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
                        end_point="ED_TR_save_change_problem",
                        last_end_point=callback_data.last_end_point,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def ed_close_request_kb(
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
                    end_point="ED_TR_close_request_description",
                ).pack(),
            ),
            InlineKeyboardButton(text=f"{description}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="Отмена",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="ED_TR_show_form_active",
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
                        end_point="ED_TR_save_close_request",
                    ).pack(),
                ),
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# endregion


# region Territorial director

td_button = InlineKeyboardButton(
    text="Технические заявки ТД", callback_data="get_TD_TR"
)

td_menu_button = InlineKeyboardButton(text="Назад", callback_data="get_TD_TR_menu")

td_pending = InlineKeyboardButton(
    text="Ожидающие заявки", callback_data="get_TD_TR_pending"
)

td_history = InlineKeyboardButton(
    text="История заявок", callback_data="get_TD_TR_history"
)

td_change_department_button = InlineKeyboardButton(
    text="Выбрать предприятие",
    callback_data="set_TD_TR_department",
)

td_change_department_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [td_change_department_button],
        [main_menu_button],
    ]
)

td_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [td_pending],
        [td_history],
        [td_button],
    ]
)


async def td_approval_form_kb(
    state: FSMContext, callback_data: ShowRequestCallbackData
) -> InlineKeyboardMarkup:
    description = (await state.get_data()).get("description")
    correct_options = (await state.get_data()).get("correct")
    form_complete = True
    if description is None:
        description = ""
        form_complete = False
    else:
        if len(description) > 16:
            description = description[:16] + "..."
        description += " ✅"

    if correct_options is None:
        correct_options = "Да/Нет"
    else:
        correct_options = f"{'Да' if correct_options else 'Нет'} ✅"

    buttons = [
        [
            InlineKeyboardButton(
                text="Статус корректен:",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="TD_TR_get_correct",
                ).pack(),
            ),
            InlineKeyboardButton(text=f"{correct_options}", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(
                text="Комментарий",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="TD_TR_get_description",
                ).pack(),
            ),
            InlineKeyboardButton(text=f"{description}", callback_data="dummy"),
        ],
    ]

    if form_complete:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Утвердить",
                    callback_data=ShowRequestCallbackData(
                        request_id=callback_data.request_id,
                        end_point="TD_TR_save_approval_form",
                    ).pack(),
                ),
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text=back,
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="TD_TR_show_pending_form",
                ).pack(),
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# region Universal


def create_kb_with_end_point_TR(
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
                            request_id=request.id,
                            end_point=end_point,
                            req_type=RequestType.TR.value,
                        ).pack(),
                    )
                ]
            )
    finally:
        buttons.append([menu_button])
        return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_kb_with_end_point_CR(
    requests: list[CleaningRequestSchema],
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
                            request_id=request.id,
                            end_point=end_point,
                            req_type=RequestType.CR.value,
                        ).pack(),
                    )
                ]
            )
    finally:
        buttons.append([menu_button])
        return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_kb_with_end_point_and_symbols(
    requests: list[TechnicalRequestSchema],
    end_point: str,
    menu_button: InlineKeyboardButton,
) -> InlineKeyboardMarkup:
    from app.infra.database.models import ApprovalStatus

    buttons: list[list[InlineKeyboardButton]] = []
    try:
        for request in requests:
            symbol = "🆗"
            match request.state:
                case ApprovalStatus.pending:
                    symbol = "⚒️"
                case ApprovalStatus.pending_approval:
                    symbol = "🔴"
                case ApprovalStatus.not_relevant:
                    symbol = "⛔️"
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{symbol} {request.department.name} {request.id} \
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
