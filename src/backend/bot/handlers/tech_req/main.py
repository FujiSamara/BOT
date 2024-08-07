from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InputMediaDocument,
    BufferedInputFile,
)
from aiogram.fsm.context import FSMContext

from db.service import get_technical_request_by_id

from bot.handlers.tech_req import worker, repairman, kru
from bot.handlers.tech_req.utils import send_photos
from bot.handlers.tech_req.schemas import ShowRequestCallbackData

router = Router(name="technical_request_main")

router.include_routers(worker.router, repairman.router, kru.router)


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "problem_docs"))
async def problem_documents(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    media: list[InputMediaDocument] = []
    request = get_technical_request_by_id(callback_data.request_id)
    for photo in request.problem_photos:
        media.append(
            InputMediaDocument(
                media=BufferedInputFile(
                    file=await photo.document.read(), filename=photo.document.filename
                )
            )
        )
    await send_photos(
        callback=callback,
        state=state,
        callback_data=callback_data,
        media=media,
        request_id=request.id,
    )


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "repair_docs"))
async def repair_documents(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    media: list[InputMediaDocument] = []
    request = get_technical_request_by_id(callback_data.request_id)
    for photo in request.repair_photos:
        media.append(
            InputMediaDocument(
                media=BufferedInputFile(
                    file=await photo.document.read(), filename=photo.document.filename
                )
            )
        )
    await send_photos(
        callback=callback,
        state=state,
        callback_data=callback_data,
        media=media,
        request_id=request.id,
    )
