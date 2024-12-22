from asyncio import sleep
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from app.services import get_workers_subordinate, get_worker_by_id, update_worker_state
from app.adapters.bot.handlers.utils import (
    try_edit_or_answer,
    try_delete_message,
    create_reply_keyboard,
)
from app.adapters.bot.handlers.worker_bids.schemas import (
    WorkersCoordinationCallbackData,
)
from app.adapters.bot.states import WorkersCoordination
from app.adapters.bot.kb import (
    get_workers_coordinate_menu_btn,
    main_menu_button,
    worker_status_dict,
)
from app.adapters.bot import text

router = Router(name="workers_subordinate")


@router.callback_query(
    WorkersCoordinationCallbackData.filter(
        F.endpoint_name == get_workers_coordinate_menu_btn.callback_data
    )
)
@router.callback_query(F.data == get_workers_coordinate_menu_btn.callback_data)
async def get_menu(
    message: Message | CallbackQuery,
    callback_data: WorkersCoordinationCallbackData = WorkersCoordinationCallbackData(),
):
    if isinstance(message, CallbackQuery):
        message = message.message

    subordinates = get_workers_subordinate(message.chat.id, 10, callback_data.page)
    buttons = []
    for subordinate in subordinates:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{subordinate.l_name} {subordinate.f_name[0]}. {subordinate.o_name[0]}.",
                    callback_data=WorkersCoordinationCallbackData(
                        id=subordinate.id,
                        page=callback_data.page,
                        endpoint_name="show_worker",
                    ).pack(),
                )
            ]
        )
    if callback_data.page > 1:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Предыдущая страница",
                    callback_data=WorkersCoordinationCallbackData(
                        page=callback_data.page - 1,
                        endpoint_name=get_workers_coordinate_menu_btn.callback_data,
                    ).pack(),
                )
            ]
        )
    if len(subordinates) == 10:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Следующая страница",
                    callback_data=WorkersCoordinationCallbackData(
                        page=callback_data.page + 1,
                        endpoint_name=get_workers_coordinate_menu_btn.callback_data,
                    ).pack(),
                )
            ]
        )
    await try_edit_or_answer(
        message=message,
        text=hbold(get_workers_coordinate_menu_btn.text),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons + [[main_menu_button]]
        ),
    )


@router.callback_query(
    WorkersCoordinationCallbackData.filter(F.endpoint_name == "show_worker")
)
async def show_worker(
    message: Message | CallbackQuery, callback_data: WorkersCoordinationCallbackData
):
    if isinstance(message, CallbackQuery):
        message = message.message
    worker = get_worker_by_id(callback_data.id)
    await try_edit_or_answer(
        message=message,
        text=f"""{worker.l_name} {worker.f_name} {worker.o_name}
{hbold('Должность:')} {worker.post.name}
{hbold('Предприятие:')} {worker.department.name}
{hbold('Номер телефона:')} {worker.phone_number}
{hbold('Статус:')} {worker_status_dict[worker.state]}""",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Изменить статус",
                        callback_data=WorkersCoordinationCallbackData(
                            id=callback_data.id,
                            page=callback_data.page,
                            endpoint_name="change_status",
                        ).pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=text.back,
                        callback_data=WorkersCoordinationCallbackData(
                            id=callback_data.id,
                            page=callback_data.page,
                            endpoint_name=get_workers_coordinate_menu_btn.callback_data,
                        ).pack(),
                    )
                ],
            ]
        ),
    )


@router.callback_query(
    WorkersCoordinationCallbackData.filter(F.endpoint_name == "change_status")
)
async def get_status(
    message: Message | CallbackQuery,
    state: FSMContext,
    callback_data: WorkersCoordinationCallbackData | None = None,
):
    if isinstance(message, CallbackQuery):
        message = message.message
    if callback_data is not None:
        await state.update_data(id=callback_data.id, page=callback_data.page)
    msg = await try_edit_or_answer(
        message=message,
        text=hbold("Выберите статус"),
        reply_markup=create_reply_keyboard(text.back, *worker_status_dict.values()),
        return_message=True,
    )
    await state.update_data(msg=msg)
    await state.set_state(WorkersCoordination.state)


@router.message(WorkersCoordination.state)
async def set_status(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_delete_message(data.get("msg"))
    await try_delete_message(message=message)
    if message.text == text.back:
        await show_worker(
            message,
            WorkersCoordinationCallbackData(
                id=int(data.get("id")),
                endpoint_name="show_worker",
                page=int(data.get("page")),
            ),
        )
    elif message.text in worker_status_dict.values():
        status = [
            key for key, text in worker_status_dict.items() if message.text == text
        ][0]
        update_worker_state(data.get("id"), state=status)
        await show_worker(
            message,
            WorkersCoordinationCallbackData(
                id=int(data.get("id")),
                endpoint_name="show_worker",
                page=int(data.get("page")),
            ),
        )
    else:
        await try_edit_or_answer(
            message=message, text=text.format_err, return_message=True
        )
        await sleep(3)
        await get_status(message=message, state=state, callback_data=None)
