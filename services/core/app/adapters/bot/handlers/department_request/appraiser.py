from asyncio import sleep
from typing import Callable
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from app.adapters.bot import text, kb
from app.adapters.bot.states import (
    Base,
    AppraiserRequestForm,
)

from app.adapters.bot.handlers.department_request.utils import (
    handle_department,
    show_form_technician,
    show_form_cleaning,
    department_names_with_count,
)
from app.adapters.bot.handlers.department_request.schemas import (
    ShowRequestCallbackData,
    RequestType,
)
from app.adapters.bot.handlers.department_request import kb as department_kb
from app.adapters.bot.handlers.utils import (
    try_delete_message,
    try_edit_or_answer,
)


from app.services import (
    get_all_history_technical_requests_for_appraiser,
    get_all_history_cleaning_requests_for_appraiser,
    get_all_waiting_technical_requests_for_appraiser,
    get_all_waiting_cleaning_requests_for_appraiser,
    get_departments_names_for_appraiser,
    update_technical_request_from_appraiser,
    update_cleaning_request_from_appraiser,
)
from app.infra.database.models import ApprovalStatus

router = Router(name="department_request_appraiser")


class CoordinationFactory:
    def __init__(
        self,
        router: Router,
        problem_type: RequestType,
        menu_button: InlineKeyboardButton,
    ):
        self.problem_type = problem_type
        self.department_menu_button = menu_button
        change_department_button = InlineKeyboardButton(
            text="Выбрать предприятие",
            callback_data=f"set_{self.problem_type.name}_department_TM",
        )
        self.change_department_menu = kb.create_inline_keyboard(
            change_department_button,
            kb.main_menu_button,
        )

        self.waiting_button = InlineKeyboardButton(
            text="Ожидающие заявки",
            callback_data=f"get_{self.problem_type.name}_waiting_TM",
        )
        self.history_button = InlineKeyboardButton(
            text="История заявок",
            callback_data=f"get_{self.problem_type.name}_history_TM",
        )
        self.menu_button = InlineKeyboardButton(
            text=text.back, callback_data=f"get_{self.problem_type.name}_menu_TM"
        )
        self.menu_markup = kb.create_inline_keyboard(
            self.waiting_button,
            self.history_button,
            InlineKeyboardButton(
                text=text.back, callback_data=menu_button.callback_data
            ),
        )

        router.callback_query.register(
            self.show_department_menu,
            F.data == self.department_menu_button.callback_data,
        )
        router.callback_query.register(
            self.change_department, F.data == change_department_button.callback_data
        )
        router.callback_query.register(
            self.show_menu, F.data == self.menu_button.callback_data
        )
        router.callback_query.register(
            self.show_history_menu, F.data == self.history_button.callback_data
        )
        router.callback_query.register(
            self.show_history_form,
            ShowRequestCallbackData.filter(
                F.end_point == f"{self.problem_type.name}_show_form_history_TM"
            ),
        )
        router.callback_query.register(
            self.show_waiting_menu, F.data == self.waiting_button.callback_data
        )
        router.callback_query.register(
            self.show_waiting_form,
            ShowRequestCallbackData.filter(
                F.end_point == f"{self.problem_type.name}_show_waiting_form_AR"
            ),
        )
        router.callback_query.register(
            self.show_rate_form,
            ShowRequestCallbackData.filter(
                F.end_point == f"{self.problem_type.name}_rate_form_AR",
            ),
        )
        router.callback_query.register(
            self.show_rate_request,
            ShowRequestCallbackData.filter(
                F.end_point == f"{self.problem_type.name}_rate_AR",
            ),
        )
        router.callback_query.register(
            self.get_description,
            ShowRequestCallbackData.filter(
                F.end_point == f"{self.problem_type.name}_description_AR"
            ),
        )
        router.callback_query.register(
            self.save_rate,
            ShowRequestCallbackData.filter(
                F.end_point == f"{self.problem_type.name}_save_rate_AR"
            ),
        )

    async def show_department_menu(self, message: Message | CallbackQuery):
        if isinstance(message, CallbackQuery):
            message = message.message

        await try_edit_or_answer(
            message=message,
            text=hbold(self.department_menu_button.text),
            reply_markup=self.change_department_menu,
        )

    async def change_department(self, callback: CallbackQuery, state: FSMContext):
        await state.set_state(AppraiserRequestForm.department)
        await state.update_data(
            generator=self.show_department_menu,
            menu_markup=self.menu_markup,
            problem_type=self.problem_type,
        )
        department_names = department_names_with_count(
            state=ApprovalStatus.pending_approval,
            tg_id=callback.message.chat.id,
            department_names=get_departments_names_for_appraiser(
                callback.message.chat.id
            ),
            type=self.problem_type,
        )

        await try_delete_message(callback.message)
        msg = await callback.message.answer(
            text=hbold("Выберите предприятие:"),
            reply_markup=kb.create_reply_keyboard(text.back, *department_names),
        )
        await state.update_data(msg=msg)

    async def show_menu(self, callback: CallbackQuery, state: FSMContext):
        department_name = (await state.get_data()).get("department_name")
        await try_edit_or_answer(
            message=callback.message,
            text=hbold(f"Предприятие: {department_name}"),
            reply_markup=self.menu_markup,
        )

    async def show_history_menu(self, callback: CallbackQuery, state: FSMContext):
        department_name = (await state.get_data()).get("department_name")
        match self.problem_type:
            case RequestType.TR:
                reply_markup = (
                    department_kb.create_kb_with_end_point_TR(
                        end_point=f"{self.problem_type.name}_show_form_history_TM",
                        menu_button=self.menu_button,
                        requests=(
                            get_all_history_technical_requests_for_appraiser(
                                tg_id=callback.message.chat.id,
                                department_name=department_name,
                            )
                        ),
                    ),
                )
            case RequestType.CR:
                reply_markup = department_kb.create_kb_with_end_point_CR(
                    end_point=f"{self.problem_type.name}_show_form_history_TM",
                    menu_button=self.menu_button,
                    requests=get_all_history_cleaning_requests_for_appraiser(
                        tg_id=callback.message.chat.id,
                        department_name=department_name,
                    ),
                )
            case _:
                reply_markup = None

        await try_delete_message(callback.message)
        await try_edit_or_answer(
            message=callback.message,
            text=hbold("История заявок"),
            reply_markup=reply_markup,
        )

    async def show_history_form(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ShowRequestCallbackData,
    ):
        buttons: list[list[InlineKeyboardButton]] = []
        match self.problem_type:
            case RequestType.TR:
                await show_form_technician(
                    callback=callback,
                    callback_data=callback_data,
                    state=state,
                    buttons=buttons,
                    history_or_waiting_button=self.history_button,
                )
            case RequestType.CR:
                await show_form_cleaning(
                    callback=callback,
                    callback_data=callback_data,
                    state=state,
                    buttons=buttons,
                    history_or_waiting_button=self.history_button,
                )

    async def show_waiting_menu(self, callback: CallbackQuery, state: FSMContext):
        department_name = (await state.get_data()).get("department_name")

        match self.problem_type:
            case RequestType.TR:
                reply_markup = department_kb.create_kb_with_end_point_TR(
                    end_point=f"{self.problem_type.name}_show_waiting_form_AR",
                    menu_button=self.menu_button,
                    requests=get_all_waiting_technical_requests_for_appraiser(
                        telegram_id=callback.message.chat.id,
                        department_name=department_name,
                    ),
                )
            case RequestType.CR:
                reply_markup = department_kb.create_kb_with_end_point_CR(
                    end_point=f"{self.problem_type.name}_show_waiting_form_AR",
                    menu_button=self.menu_button,
                    requests=get_all_waiting_cleaning_requests_for_appraiser(
                        tg_id=callback.message.chat.id,
                        department_name=department_name,
                    ),
                )
            case _:
                reply_markup = []

        await try_delete_message(callback.message)
        await try_edit_or_answer(
            message=callback.message,
            text=hbold("Ожидающие заявки"),
            reply_markup=reply_markup,
        )

    async def show_waiting_form(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ShowRequestCallbackData,
    ):
        buttons: list[list[InlineKeyboardButton]] = [
            [
                InlineKeyboardButton(
                    text="Оценить заявку",
                    callback_data=ShowRequestCallbackData(
                        request_id=callback_data.request_id,
                        end_point=f"{self.problem_type.name}_rate_form_AR",
                    ).pack(),
                )
            ]
        ]
        match self.problem_type:
            case RequestType.TR:
                await show_form_technician(
                    callback=callback,
                    callback_data=callback_data,
                    state=state,
                    buttons=buttons,
                    history_or_waiting_button=self.waiting_button,
                )
            case RequestType.CR:
                await show_form_cleaning(
                    callback=callback,
                    callback_data=callback_data,
                    state=state,
                    buttons=buttons,
                    history_or_waiting_button=self.waiting_button,
                )

    async def show_rate_form(
        self,
        message: Message | CallbackQuery,
        state: FSMContext,
        callback_data: ShowRequestCallbackData | None = None,
    ):
        if isinstance(message, CallbackQuery):
            message = message.message
        else:
            data = await state.get_data()

            callback_data = ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point=f"{self.problem_type.name}_rate_form_AR",
            )
        await try_edit_or_answer(
            message=message,
            text=hbold("Оценить заявку"),
            reply_markup=await department_kb.tm_rate_kb(
                state=state, callback_data=callback_data, problem_type=self.problem_type
            ),
        )

    async def show_rate_request(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ShowRequestCallbackData,
    ):
        await state.set_state(AppraiserRequestForm.mark)
        await state.update_data(
            request_id=callback_data.request_id,
            generator=self.show_rate_form,
        )
        await try_delete_message(callback.message)
        msg = await callback.message.answer(
            text=hbold("Оценка:"),
            reply_markup=kb.create_reply_keyboard(
                text.back, *[str(mark) for mark in range(1, 6)]
            ),
        )
        await state.update_data(msg=msg)

    async def get_description(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ShowRequestCallbackData,
    ):
        await state.set_state(AppraiserRequestForm.description)
        await try_delete_message(callback.message)
        msg = await callback.message.answer(text=hbold("Введите комментарий:"))
        await state.update_data(msg=msg, generator=self.show_rate_form)

    async def save_rate(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ShowRequestCallbackData,
    ):
        data = await state.get_data()
        mark = data.get("mark")
        description = data.get("description")
        request_id = callback_data.request_id

        message = callback.message
        match self.problem_type:
            case RequestType.TR:
                update: Callable = update_technical_request_from_appraiser
            case RequestType.CR:
                update: Callable = update_cleaning_request_from_appraiser

        if not await update(mark=mark, request_id=request_id, description=description):
            message = await try_edit_or_answer(
                message=callback.message,
                text="Упс, произошла ошибка.",
                return_message=True,
            )
            await sleep(2)
            await try_delete_message(message=message)

        await state.clear()
        await state.set_state(Base.none)
        await try_edit_or_answer(
            message=message,
            text=hbold(self.department_menu_button.text),
            reply_markup=self.change_department_menu,
        )


@router.message(AppraiserRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    data = await state.get_data()
    if "menu_markup" not in data:
        raise KeyError("menu_markup in department request not exist")
    if "generator" not in data:
        raise KeyError("generator in department request not exist")
    if "problem_type" not in data:
        raise KeyError("generator in department request not exist")
    problem_type: RequestType = data.get("problem_type")
    show_department_menu: Callable = data.get("generator")
    menu_markup: InlineKeyboardMarkup = data.get("menu_markup")
    department_names = department_names_with_count(
        state=ApprovalStatus.pending_approval,
        tg_id=message.chat.id,
        department_names=get_departments_names_for_appraiser(message.chat.id),
        type=problem_type,
    )

    if await handle_department(
        message=message,
        state=state,
        departments_names=department_names,
        reply_markup=menu_markup,
    ):
        await show_department_menu(message)


@router.message(AppraiserRequestForm.description)
async def set_description(message: Message, state: FSMContext):
    await state.set_state(Base.none)
    data = await state.get_data()
    msg: Message = data.get("msg")
    if "generator" not in data:
        raise KeyError("generator in department request not exist")
    show_rate_form: Callable = data.get("generator")
    if msg:
        await try_delete_message(msg)
    await state.update_data(description=message.text)
    await try_delete_message(message)
    await show_rate_form(message, state)


@router.message(AppraiserRequestForm.mark)
async def set_mark(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if "generator" not in data:
        raise KeyError("generator in department request not exist")
    show_rate_form: Callable = data.get("generator")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await state.set_state(Base.none)
        await show_rate_form(message=message, state=state)
    else:
        if int(message.text) not in range(1, 6):
            msg = await message.answer(
                text=text.format_err,
                reply_markup=kb.create_reply_keyboard(
                    *[str(mark) for mark in range(1, 6)]
                ),
            )
            await state.update_data(msg=msg)
            return
        await state.update_data(mark=int(message.text))
        await show_rate_form(message=message, state=state)
        await state.set_state(Base.none)


def build_coordinations():
    CoordinationFactory(
        router=router,
        problem_type=RequestType.TR,
        menu_button=department_kb.AR_TR_button,
    )
    CoordinationFactory(
        router=router,
        problem_type=RequestType.CR,
        menu_button=department_kb.AR_CR_button,
    )
