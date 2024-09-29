from aiogram import F, Router
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaDocument, Message
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
import asyncio
from typing import Any, Callable

from bot.kb import (
    main_menu_button,
    create_inline_keyboard,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    kru_dismissal_menu_button,
    access_dismissal_menu_button,
    accountant_dismissal_menu_button,
    tech_dismissal_menu_button,
)

from db.models import Dismissal
from db.service import (
    get_pending_dismissal_blanks_by_column,
    get_dismissal_by_id,
    update_dismissal,
)
from bot.handlers.dismissal.schemas import (
    DismissalCallbackData,
    DismissalActionData,
    ActionType,
)
from bot.states import DismissalCoordination
from bot.handlers.dismissal.utils import (
    get_dismissal_list_info,
    get_dismissal_blank_info,
)
from bot.handlers.utils import try_delete_message, try_edit_message

router = Router(name="dismissal_coordination")


class DismissalCoordinationFactory:
    def __init__(
        self,
        router: Router,
        name: str,
        coordinator_menu_button: InlineKeyboardButton,
        state_column: Any,
    ):
        self.name = name
        self.coordinator_menu_button = coordinator_menu_button
        self.approving_endpoint_name = f"{name}_dismissal_approving"
        self.documents_endpoint_name = f"{name}_dismissal_documents"
        self.state_column = state_column
        self.pending_button = InlineKeyboardButton(
            text="Ожидающие заявки", callback_data=f"{name}_dismissal_pending"
        )

        router.callback_query.register(
            self.get_menu, F.data == coordinator_menu_button.callback_data
        )
        router.callback_query.register(
            self.get_pendings, F.data == f"{name}_dismissal_pending"
        )
        router.callback_query.register(
            self.get_dismissal_blank,
            DismissalCallbackData.filter(F.endpoint_name == self.name),
        )
        router.callback_query.register(
            self.get_documents,
            DismissalCallbackData.filter(
                F.endpoint_name == self.documents_endpoint_name
            ),
        )
        router.callback_query.register(
            self.approve_dismissal,
            DismissalActionData.filter(F.action == ActionType.approving),
            DismissalActionData.filter(F.endpoint_name == self.approving_endpoint_name),
        )
        router.callback_query.register(
            self.comment_dismissal,
            DismissalActionData.filter(F.action == ActionType.declining),
            DismissalActionData.filter(F.endpoint_name == self.approving_endpoint_name),
        )

    async def get_menu(self, callback: CallbackQuery):
        keyboard = create_inline_keyboard(self.pending_button, main_menu_button)
        await try_edit_message(
            message=callback.message,
            text="Согласование увольнений",
            reply_markup=keyboard,
        )

    async def get_pendings(self, callback: CallbackQuery):
        keyboard = self.get_pending_dismissal_keyboard()
        await try_delete_message(callback.message)
        await callback.message.answer("Ожидающие согласования:", reply_markup=keyboard)

    async def approve_dismissal(
        self,
        callback: CallbackQuery,
        callback_data: DismissalActionData,
        state: FSMContext,
    ):
        data = await state.get_data()
        comment = data.get("comment")
        dismissal = get_dismissal_by_id(callback_data.dismissal_id)

        update_dismissal(dismissal, self.state_column.name, comment)

        msg = await callback.message.answer(text="Успешно!")
        await asyncio.sleep(1)
        await msg.delete()
        await self.get_pendings(callback)

    async def comment_dismissal(
        self,
        callback: CallbackQuery,
        callback_data: DismissalActionData,
        state: FSMContext,
    ):
        dismissal = get_dismissal_by_id(callback_data.dismissal_id)
        await try_edit_message(callback.message, hbold("Введите причину отказа:"))
        await state.set_state(DismissalCoordination.comment)
        await state.update_data(
            generator=self.get_dismissal_blank,
            callback=callback,
            dismissal=dismissal,
            column_name=self.state_column.name,
            callback_data=DismissalCallbackData(
                id=callback_data.dismissal_id, endpoint_name=self.name
            ),
        )

    def get_pending_dismissal_keyboard(self) -> InlineKeyboardMarkup:
        blanks = []
        blanks = get_pending_dismissal_blanks_by_column(self.state_column)
        blanks = sorted(blanks, key=lambda blank: blank.create_date, reverse=True)[:10]
        return create_inline_keyboard(
            *(
                InlineKeyboardButton(
                    text=get_dismissal_list_info(blank),
                    callback_data=DismissalCallbackData(
                        id=blank.id,
                        endpoint_name=self.name,
                    ).pack(),
                )
                for blank in blanks
            ),
            self.coordinator_menu_button,
        )

    async def get_documents(
        self,
        callback: CallbackQuery,
        callback_data: DismissalCallbackData,
        state: FSMContext,
    ):
        blank = get_dismissal_by_id(callback_data.id)
        media: list[InputMediaDocument] = []

        for document in blank.documents:
            media.append(
                InputMediaDocument(
                    media=BufferedInputFile(
                        file=document.document.file.read(),
                        filename=document.document.filename,
                    ),
                )
            )
        await try_delete_message(callback.message)
        msgs = await callback.message.answer_media_group(media=media)
        await state.update_data(msgs_for_delete=msgs)
        await msgs[0].reply(
            text=hbold("Выберите действие:"),
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=DismissalCallbackData(
                        id=blank.id,
                        endpoint_name=self.name,
                    ).pack(),
                )
            ),
        )

    async def get_dismissal_blank(
        self,
        callback: CallbackQuery,
        callback_data: DismissalCallbackData,
        state: FSMContext,
    ):
        blank = get_dismissal_by_id(callback_data.id)
        data = await state.get_data()
        comment_text = "Комментарий"
        if data.get("comment"):
            comment_text += " ✅"
        if "msgs_for_delete" in data:
            for msg in data["msgs_for_delete"]:
                await try_delete_message(msg)
            await state.update_data(msgs_for_delete=[])

        caption = get_dismissal_blank_info(blank)

        buttons = [
            InlineKeyboardButton(
                text="Показать документы",
                callback_data=DismissalCallbackData(
                    id=blank.id,
                    endpoint_name=self.documents_endpoint_name,
                ).pack(),
            ),
            InlineKeyboardButton(
                text="Согласовать",
                callback_data=DismissalActionData(
                    dismissal_id=blank.id,
                    action=ActionType.approving,
                    endpoint_name=self.approving_endpoint_name,
                ).pack(),
            ),
            InlineKeyboardButton(
                text=comment_text,
                callback_data=DismissalActionData(
                    dismissal_id=blank.id,
                    action=ActionType.declining,
                    endpoint_name=self.approving_endpoint_name,
                ).pack(),
            ),
            self.pending_button,
        ]
        await try_edit_message(
            message=callback.message,
            text=caption,
            reply_markup=create_inline_keyboard(*buttons),
        )


@router.message(DismissalCoordination.comment)
async def comment_decline(message: Message, state: FSMContext):
    data = await state.get_data()
    if "generator" not in data:
        raise KeyError("Pending generator not exist")
    if "callback" not in data:
        raise KeyError("Callback not exist")
    if "dismissal" not in data:
        raise KeyError("Dismissal not exist")
    if "column_name" not in data:
        raise KeyError("Column name not exist")
    if "callback_data" not in data:
        raise KeyError("Callback data not exist")

    generator: Callable = data["generator"]
    callback: CallbackQuery = data["callback"]
    callback_data: DismissalCallbackData = data["callback_data"]
    await state.update_data(comment=message.text)

    await try_delete_message(message)
    await generator(callback, callback_data, state)


def build_coordination():
    DismissalCoordinationFactory(
        router=router,
        coordinator_menu_button=kru_dismissal_menu_button,
        state_column=Dismissal.kru_state,
        name="kru",
    )
    DismissalCoordinationFactory(
        router=router,
        coordinator_menu_button=access_dismissal_menu_button,
        state_column=Dismissal.access_state,
        name="access",
    )
    DismissalCoordinationFactory(
        router=router,
        coordinator_menu_button=accountant_dismissal_menu_button,
        state_column=Dismissal.accountant_state,
        name="accountant",
    )
    DismissalCoordinationFactory(
        router=router,
        coordinator_menu_button=tech_dismissal_menu_button,
        state_column=Dismissal.tech_state,
        name="tech",
    )
