from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext

from app.services import get_technical_request_by_id, get_cleaning_request_by_id
from app.adapters.bot.handlers.department_request.utils import (
    send_many_docs,
)
from app.adapters.bot.handlers.department_request.schemas import (
    ShowRequestCallbackData,
    RequestType,
)

router = Router()


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "TR_problem_docs"))
async def technical_problem_documents(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    request = get_technical_request_by_id(callback_data.request_id)
    await send_many_docs(
        request=request,
        doc_type="problem_photos",
        callback=callback,
        state=state,
        callback_data=callback_data,
        reopen=False,
    )


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "TR_repair_docs"))
async def repair_documents(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    request = get_technical_request_by_id(callback_data.request_id)
    await send_many_docs(
        request=request,
        doc_type="repair_photos",
        callback=callback,
        state=state,
        callback_data=callback_data,
        reopen=False,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == f"{RequestType.CR.name}_problem_docs")
)
async def cleaning_problem_documents(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    request = get_cleaning_request_by_id(callback_data.request_id)

    await send_many_docs(
        request=request,
        doc_type="problem_photos",
        callback=callback,
        state=state,
        callback_data=callback_data,
        reopen=False,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == f"{RequestType.CR.name}_repair_docs")
)
async def cleaning_documents(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    request = get_cleaning_request_by_id(callback_data.request_id)

    await send_many_docs(
        request=request,
        doc_type="cleaning_photos",
        callback=callback,
        state=state,
        callback_data=callback_data,
        reopen=False,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "TR_reopen_repair_docs")
)
async def reopen_repair_documents(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    request = get_technical_request_by_id(callback_data.request_id)

    await send_many_docs(
        request=request,
        doc_type="repair_photos",
        callback=callback,
        state=state,
        callback_data=callback_data,
        reopen=True,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(
        F.end_point == f"{RequestType.CR.name}_reopen_docs",
    )
)
async def cleaning_reopen_documents(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    request = get_cleaning_request_by_id(callback_data.request_id)

    await send_many_docs(
        request=request,
        doc_type="cleaning_photos",
        callback=callback,
        state=state,
        callback_data=callback_data,
        reopen=True,
    )
