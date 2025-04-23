from typing import Callable
from aiogram import Router, F
from asyncio import sleep
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from fastapi import UploadFile

from app.adapters.bot import text, kb
from app.adapters.bot.kb import main_menu_button
from app.adapters.bot.states import (
    Base,
    ExecutorDepartmentRequestForm,
)
from app.adapters.bot.handlers.department_request.schemas import (
    ShowRequestCallbackData,
    PageCallbackData,
    RequestType,
)
from app.adapters.bot.handlers.department_request import kb as department_kb
from app.adapters.bot.handlers.utils import (
    try_edit_or_answer,
    try_delete_message,
    download_file,
    handle_documents_form,
    handle_documents,
)
from app.adapters.bot.handlers.department_request.utils import (
    get_departments_names_executor,
    handle_department,
    show_form_technician,
    show_form_cleaning,
    department_names_with_count,
)
from app.services import (
    get_all_history_technical_requests_for_repairman,
    get_all_history_cleaning_requests_for_cleaner,
    get_all_rework_technical_requests_for_repairman,
    get_all_rework_cleaning_requests_for_cleaner,
    get_all_waiting_technical_requests_for_repairman,
    get_all_waiting_cleaning_requests_for_cleaner,
    update_technical_request_from_repairman,
    update_cleaning_request_from_cleaner,
)
from app.infra.database.models import ApprovalStatus

router = Router(name="department_request_executors")


class CoordinationFactory:
    def __init__(
        self,
        router: Router,
        problem_type: RequestType,
        executor_menu_button: InlineKeyboardButton,
    ):
        self.type = problem_type
        self.name = problem_type.name
        self.executor_menu_button = executor_menu_button
        change_department_button = InlineKeyboardButton(
            text="Выбрать предприятие",
            callback_data=f"set_executor_{self.name}_department",
        )
        self.change_department_menu = kb.create_inline_keyboard(
            change_department_button,
            main_menu_button,
        )

        self.waiting_button = InlineKeyboardButton(
            text="Ожидающие заявки", callback_data=f"get_executor_{self.name}_waiting"
        )
        self.rework_button = InlineKeyboardButton(
            text="Заявки на доработку", callback_data=f"get_executor_{self.name}_rework"
        )
        self.history_button = InlineKeyboardButton(
            text="История заявок", callback_data=f"get_executor_{self.name}_history"
        )
        self.menu_button = InlineKeyboardButton(
            text=text.back, callback_data=f"get_{self.name}_executor_menu"
        )
        self.menu_markup = kb.create_inline_keyboard(
            self.waiting_button,
            self.rework_button,
            self.history_button,
            InlineKeyboardButton(
                text=text.back, callback_data=executor_menu_button.callback_data
            ),
        )

        router.callback_query.register(
            self.show_department_menu, F.data == executor_menu_button.callback_data
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
            self.show_history_menu,
            PageCallbackData.filter(
                F.requests_endpoint == self.history_button.callback_data
            ),
        )
        router.callback_query.register(
            self.show_history_form,
            ShowRequestCallbackData.filter(
                F.end_point == f"{self.name}_show_history_form"
            ),
        )
        router.callback_query.register(
            self.show_waiting_menu, F.data == self.waiting_button.callback_data
        )

        router.callback_query.register(
            self.show_waiting_menu,
            PageCallbackData.filter(
                F.requests_endpoint == self.waiting_button.callback_data
            ),
        )
        router.callback_query.register(
            self.show_waiting_form,
            ShowRequestCallbackData.filter(
                F.end_point == f"{self.name}_show_waiting_form"
            ),
        )
        router.callback_query.register(
            self.show_waiting_work,
            ShowRequestCallbackData.filter(
                F.end_point == f"{self.name}_waiting_work_form"
            ),
        )
        router.callback_query.register(
            self.get_waiting_photo,
            ShowRequestCallbackData.filter(
                F.end_point == f"get_{self.name}_waiting_photo"
            ),
        )
        router.callback_query.register(
            self.show_rework_menu, F.data == self.rework_button.callback_data
        )
        router.callback_query.register(
            self.show_rework_menu,
            PageCallbackData.filter(
                F.requests_endpoint == self.rework_button.callback_data
            ),
        )
        router.callback_query.register(
            self.show_rework_form,
            ShowRequestCallbackData.filter(
                F.end_point == f"{self.name}_show_rework_form"
            ),
        )
        router.callback_query.register(
            self.show_repair_rework_form,
            ShowRequestCallbackData.filter(
                F.end_point == f"{self.name}_repair_rework_form"
            ),
        )
        router.callback_query.register(
            self.get_rework_photo,
            ShowRequestCallbackData.filter(
                F.end_point == f"get_{self.name}_rework_photo"
            ),
        )
        router.callback_query.register(
            self.save_work,
            ShowRequestCallbackData.filter(F.end_point == f"save_{self.name}_work"),
        )

    async def show_department_menu(self, message: Message | CallbackQuery):
        if isinstance(message, CallbackQuery):
            message = message.message
        await try_edit_or_answer(
            message=message,
            text=hbold(self.executor_menu_button.text),
            reply_markup=self.change_department_menu,
        )

    async def change_department(self, callback: CallbackQuery, state: FSMContext):
        await state.set_state(ExecutorDepartmentRequestForm.department)
        await state.update_data(
            generator=self.show_department_menu,
            type=self.type,
            menu_data=self.executor_menu_button.callback_data,
        )
        department_names = department_names_with_count(
            state=ApprovalStatus.pending,
            tg_id=callback.message.chat.id,
            department_names=get_departments_names_executor(
                tg_id=callback.message.chat.id, type=self.type
            ),
            type=self.type,
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

    async def show_history_menu(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: PageCallbackData = PageCallbackData(page=0),
    ):
        department_name = (await state.get_data()).get("department_name")
        match self.type:
            case RequestType.TR:
                reply_markup = department_kb.create_kb_with_end_point_TR(
                    end_point=f"{self.name}_show_history_form",
                    menu_button=self.menu_button,
                    requests=get_all_history_technical_requests_for_repairman(
                        telegram_id=callback.message.chat.id,
                        department_name=department_name,
                        page=callback_data.page,
                    ),
                    page=callback_data.page,
                    requests_endpoint=self.history_button.callback_data,
                )
            case RequestType.CR:
                reply_markup = department_kb.create_kb_with_end_point_CR(
                    end_point=f"{self.name}_show_history_form",
                    menu_button=self.menu_button,
                    requests=get_all_history_cleaning_requests_for_cleaner(
                        tg_id=callback.message.chat.id,
                        department_name=department_name,
                        page=callback_data.page,
                    ),
                    page=callback_data.page,
                    requests_endpoint=self.history_button.callback_data,
                )
            case _:
                reply_markup = []

        await try_delete_message(callback.message)
        await try_edit_or_answer(
            message=callback.message,
            text=hbold("История заявок.")
            + f"\nПредприятие: {department_name}\nСтраница :{callback_data.page + 1}",
            reply_markup=reply_markup,
        )

    async def show_history_form(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ShowRequestCallbackData,
    ):
        buttons: list[list[InlineKeyboardButton]] = []
        match self.type:
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

    async def show_waiting_menu(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: PageCallbackData = PageCallbackData(page=0),
    ):
        department_name = (await state.get_data()).get("department_name")
        match self.type:
            case RequestType.TR:
                reply_markup = department_kb.create_kb_with_end_point_TR(
                    end_point=f"{self.name}_show_waiting_form",
                    menu_button=self.menu_button,
                    requests=get_all_waiting_technical_requests_for_repairman(
                        telegram_id=callback.message.chat.id,
                        department_name=department_name,
                        page=callback_data.page,
                    ),
                    page=callback_data.page,
                    requests_endpoint=self.waiting_button.callback_data,
                )
            case RequestType.CR:
                reply_markup = department_kb.create_kb_with_end_point_CR(
                    end_point=f"{self.name}_show_waiting_form",
                    menu_button=self.menu_button,
                    requests=get_all_waiting_cleaning_requests_for_cleaner(
                        tg_id=callback.message.chat.id,
                        department_name=department_name,
                        page=callback_data.page,
                    ),
                    page=callback_data.page,
                    requests_endpoint=self.waiting_button.callback_data,
                )
            case _:
                reply_markup = []

        await try_delete_message(callback.message)

        await try_edit_or_answer(
            message=callback.message,
            text=hbold("Ожидающие заявки")
            + f"\nПредприятие: {department_name}\nСтраница :{callback_data.page + 1}",
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
                    text="Выполнить заявку",
                    callback_data=ShowRequestCallbackData(
                        request_id=callback_data.request_id,
                        end_point=f"{self.name}_waiting_work_form",
                    ).pack(),
                )
            ]
        ]
        match self.type:
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

    async def show_waiting_work(
        self,
        message: CallbackQuery | Message,
        state: FSMContext,
        callback_data: ShowRequestCallbackData | None = None,
    ):
        if callback_data is None:
            data = await state.get_data()
            callback_data = ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point=f"{self.name}_waiting_work_form",
            )
        if isinstance(message, CallbackQuery):
            message = message.message
        await try_edit_or_answer(
            message=message,
            text=hbold("Выполнить заявку"),
            reply_markup=await department_kb.executer_work_waiting_kb(
                state=state, callback_data=callback_data, executor_type=self.type
            ),
        )

    async def get_waiting_photo(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ShowRequestCallbackData,
    ):
        await state.update_data(
            request_id=callback_data.request_id, generator=self.show_waiting_work
        )
        await handle_documents_form(
            callback.message, state, ExecutorDepartmentRequestForm.photo_waiting
        )

    async def show_rework_menu(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: PageCallbackData = PageCallbackData(page=0),
    ):
        department_name = (await state.get_data()).get("department_name")
        match self.type:
            case RequestType.TR:
                reply_markup = department_kb.create_kb_with_end_point_TR(
                    end_point=f"{self.name}_show_rework_form",
                    menu_button=self.menu_button,
                    requests=get_all_rework_technical_requests_for_repairman(
                        telegram_id=callback.message.chat.id,
                        department_name=department_name,
                    ),
                    page=callback_data.page,
                    requests_endpoint=self.rework_button.callback_data,
                )
            case RequestType.CR:
                reply_markup = department_kb.create_kb_with_end_point_CR(
                    end_point=f"{self.name}_show_rework_form",
                    menu_button=self.menu_button,
                    requests=get_all_rework_cleaning_requests_for_cleaner(
                        tg_id=callback.message.chat.id,
                        department_name=department_name,
                    ),
                    page=callback_data.page,
                    requests_endpoint=self.rework_button.callback_data,
                )
            case _:
                reply_markup = []

        await try_delete_message(callback.message)
        await try_edit_or_answer(
            message=callback.message,
            text=hbold("Заявки на доработку")
            + f"\nПредприятие: {department_name}\nСтраница :{callback_data.page + 1}",
            reply_markup=reply_markup,
        )

    async def show_rework_form(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ShowRequestCallbackData,
    ):
        buttons: list[list[InlineKeyboardButton]] = [
            [
                InlineKeyboardButton(
                    text="Выполнить заявку",
                    callback_data=ShowRequestCallbackData(
                        request_id=callback_data.request_id,
                        end_point=f"{self.name}_repair_rework_form",
                    ).pack(),
                )
            ]
        ]
        match self.type:
            case RequestType.TR:
                await show_form_technician(
                    callback=callback,
                    callback_data=callback_data,
                    state=state,
                    buttons=buttons,
                    history_or_waiting_button=self.rework_button,
                )
            case RequestType.CR:
                await show_form_cleaning(
                    callback=callback,
                    callback_data=callback_data,
                    state=state,
                    buttons=buttons,
                    history_or_waiting_button=self.rework_button,
                )

    async def show_repair_rework_form(
        self,
        message: CallbackQuery | Message,
        state: FSMContext,
        callback_data: ShowRequestCallbackData | None = None,
    ):
        if isinstance(message, CallbackQuery):
            message = message.message

        if callback_data is None:
            data = await state.get_data()
            callback_data = ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point=f"{self.name}_repair_rework_form",
                last_end_point=f"{self.name}_show_rework_form",
            )
        await try_edit_or_answer(
            message=message,
            text=hbold("Выполнить заявку"),
            reply_markup=await department_kb.executor_repair_rework_kb(
                state=state, callback_data=callback_data, executor_type=self.type
            ),
        )

    async def get_rework_photo(
        self,
        callback: CallbackQuery,
        callback_data: ShowRequestCallbackData,
        state: FSMContext,
    ):
        await state.update_data(
            request_id=callback_data.request_id, generator=self.show_repair_rework_form
        )
        await handle_documents_form(
            callback.message, state, ExecutorDepartmentRequestForm.photo_rework
        )

    async def save_work(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ShowRequestCallbackData,
    ):
        message = callback.message

        data = await state.get_data()
        photo = data["photo"]
        photo_files: list[UploadFile] = []
        for doc in photo:
            photo_files.append(await download_file(doc))

        match self.type:
            case RequestType.TR:
                update = update_technical_request_from_repairman
            case RequestType.CR:
                update = update_cleaning_request_from_cleaner

        if not await update(
            photo_files=photo_files, request_id=callback_data.request_id
        ):
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
            message=callback.message,
            text=hbold(self.executor_menu_button.text),
            reply_markup=self.change_department_menu,
        )


@router.message(ExecutorDepartmentRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    data = await state.get_data()
    if "generator" not in data:
        raise KeyError("Menu generator in department request not exist")
    if "type" not in data:
        raise KeyError("Executor type in department request not exist")
    if "menu_data" not in data:
        raise KeyError("Menu button in department request not exist")

    type: RequestType = data.get("type")
    menu_data: InlineKeyboardButton = data.get("menu_data")

    if await handle_department(
        message=message,
        state=state,
        departments_names=department_names_with_count(
            state=ApprovalStatus.pending,
            tg_id=message.chat.id,
            department_names=get_departments_names_executor(
                tg_id=message.chat.id, type=data.get("type")
            ),
            type=data.get("type"),
        ),
        reply_markup=kb.create_inline_keyboard(
            InlineKeyboardButton(
                text="Ожидающие заявки",
                callback_data=f"get_executor_{type.name}_waiting",
            ),
            InlineKeyboardButton(
                text="Заявки на доработку",
                callback_data=f"get_executor_{type.name}_rework",
            ),
            InlineKeyboardButton(
                text="История заявок", callback_data=f"get_executor_{type.name}_history"
            ),
            InlineKeyboardButton(text=text.back, callback_data=menu_data),
        ),
    ):
        show_department_menu: Callable = data.get("generator")
        await show_department_menu(message)


@router.message(ExecutorDepartmentRequestForm.photo_waiting)
async def set_waiting_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    if "generator" not in data:
        raise
    show_waiting_work: Callable = data.get("generator")
    await handle_documents(message, state, "photo", show_waiting_work)


@router.message(ExecutorDepartmentRequestForm.photo_rework)
async def set_rework_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    if "generator" not in data:
        raise
    show_repair_rework_form: Callable = data.get("generator")
    await handle_documents(message, state, "photo", show_repair_rework_form)


def build_coordinations():
    CoordinationFactory(
        router=router,
        problem_type=RequestType.TR,
        executor_menu_button=department_kb.repairman_button,
    )
    CoordinationFactory(
        router=router,
        problem_type=RequestType.CR,
        executor_menu_button=department_kb.cleaner_button,
    )
