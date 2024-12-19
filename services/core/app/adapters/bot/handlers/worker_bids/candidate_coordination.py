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
from app.services import get_candidates, get_worker_by_id, update_worker_state
from app.adapters.bot.handlers.utils import (
    try_edit_or_answer,
    try_delete_message,
    create_reply_keyboard,
)
from app.adapters.bot.handlers.worker_bids.schemas import (
    CandidateCoordinationCallbackData,
)
from app.adapters.bot.states import CandidateCoordination
from app.adapters.bot.kb import (
    get_candidates_menu_btn,
    main_menu_button,
    worker_status_dict,
)
from app.adapters.bot import text

router = Router(name="workers_menu")


@router.callback_query(
    CandidateCoordinationCallbackData.filter(
        F.endpoint_name == get_candidates_menu_btn.callback_data
    )
)
@router.callback_query(F.data == get_candidates_menu_btn.callback_data)
async def get_menu(
    message: Message | CallbackQuery,
    callback_data: CandidateCoordinationCallbackData = CandidateCoordinationCallbackData(),
):
    if isinstance(message, CallbackQuery):
        message = message.message

    subordinates = get_candidates(message.chat.id, 10, callback_data.page)
    buttons = []
    for subordinate in subordinates:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{subordinate.l_name} {subordinate.f_name[0]}. {subordinate.o_name[0]}.",
                    callback_data=CandidateCoordinationCallbackData(
                        id=subordinate.id,
                        page=callback_data.page,
                        endpoint_name="show_candidate",
                    ).pack(),
                )
            ]
        )
    await try_edit_or_answer(
        message=message,
        text=hbold(get_candidates_menu_btn.text),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons + [[main_menu_button]]
        ),
    )


@router.callback_query(
    CandidateCoordinationCallbackData.filter(F.endpoint_name == "show_candidate")
)
async def show_candidate(
    message: Message | CallbackQuery, callback_data: CandidateCoordinationCallbackData
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
                        callback_data=CandidateCoordinationCallbackData(
                            id=callback_data.id,
                            page=callback_data.page,
                            endpoint_name="change_status",
                        ).pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=text.back,
                        callback_data=CandidateCoordinationCallbackData(
                            id=callback_data.id,
                            page=callback_data.page,
                            endpoint_name=get_candidates_menu_btn.callback_data,
                        ).pack(),
                    )
                ],
            ]
        ),
    )


@router.callback_query(
    CandidateCoordinationCallbackData.filter(F.endpoint_name == "change_status")
)
async def get_status(
    message: Message | CallbackQuery,
    state: FSMContext,
    callback_data: CandidateCoordinationCallbackData | None = None,
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
    await state.set_state(CandidateCoordination.state)


@router.message(CandidateCoordination.state)
async def set_status(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_delete_message(data.get("msg"))
    await try_delete_message(message=message)
    if message.text == text.back:
        await show_candidate(
            message,
            CandidateCoordinationCallbackData(
                id=int(data.get("id")),
                endpoint_name="show_candidate",
                page=int(data.get("page")),
            ),
        )
    elif message.text in worker_status_dict.values():
        status = [
            key for key, text in worker_status_dict.items() if message.text == text
        ][0]
        update_worker_state(data.get("id"), state=status)
        await show_candidate(
            message,
            CandidateCoordinationCallbackData(
                id=int(data.get("id")),
                endpoint_name="show_candidate",
                page=int(data.get("page")),
            ),
        )
    else:
        await try_edit_or_answer(
            message=message, text=text.format_err, return_message=True
        )
        await sleep(3)
        await get_status(message=message, state=state, callback_data=None)
