from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
import asyncio

# bot imports
from bot.kb import get_create_dismissal_blank_menu
from bot.handlers.dismissal.text import dismissal_request_text
from bot.states import Base
from bot.handlers.utils import try_edit_message

# db imports
from db.schemas import DismissalSchema


async def clear_state_with_success_employee(
    message: Message, state: FSMContext, sleep_time=1, edit=False
):
    ans = await message.answer(hbold("Успешно!"), reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(sleep_time)
    await ans.delete()
    await state.set_state(Base.none)
    if edit:
        await try_edit_message(
            message=message,
            text=hbold(dismissal_request_text),
            reply_markup=await get_create_dismissal_blank_menu(state),
        )
    else:
        await message.answer(
            hbold(dismissal_request_text),
            reply_markup=await get_create_dismissal_blank_menu(state),
        )


def with_next_line(strings: list[str]) -> str:
    string = str()
    for s in strings:
        string += s + "\n"
    return string


def get_dismissal_blank_info(blank: DismissalSchema) -> str:
    info = list()
    info.append(
        f"{blank.subordination.employee.l_name} {blank.subordination.employee.f_name} {blank.subordination.employee.o_name}"
    )
    info.append(blank.subordination.employee.post.name)
    info.append(blank.subordination.employee.department.name)

    return with_next_line(info)


def get_dismissal_list_info(blank: DismissalSchema) -> str:
    return (
        f"{blank.id}: {blank.subordination.employee.l_name} "
        + f"{blank.create_date.strftime('%d.%m.%Y')} "
        + f"{blank.subordination.employee.department.name}"
    )
