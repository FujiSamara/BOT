from aiogram import Router, F
from app.adapters.bot.handlers.tech_request.utils import send_photos
from app.adapters.bot.handlers.tech_request.schemas import ShowRequestCallbackData
from aiogram.types import (
    CallbackQuery,
    InputMediaDocument,
    BufferedInputFile,
)
from aiogram.fsm.context import FSMContext

from app.services import get_technical_request_by_id

from app.infra.config.settings import settings

router = Router()


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "TR_problem_docs"))
async def problem_documents(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    media: list[InputMediaDocument] = []
    deleted_files_count = 0
    request = get_technical_request_by_id(callback_data.request_id)

    for photo in request.problem_photos:
        if photo.document.filename != settings.stubname:
            media.append(
                InputMediaDocument(
                    media=BufferedInputFile(
                        file=await photo.document.read(),
                        filename=photo.document.filename,
                    )
                )
            )
        else:
            deleted_files_count += 1

    await send_photos(
        callback=callback,
        state=state,
        callback_data=callback_data,
        media=media,
        request_id=request.id,
        deleted_files_count=deleted_files_count,
    )


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "TR_repair_docs"))
async def repair_documents(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    media: list[InputMediaDocument] = []
    deleted_files_count = 0
    request = get_technical_request_by_id(callback_data.request_id)

    for photo in request.repair_photos:
        if photo.document.filename != settings.stubname:
            if "_reopen_" not in photo.document.filename:
                media.append(
                    InputMediaDocument(
                        media=BufferedInputFile(
                            file=await photo.document.read(),
                            filename=photo.document.filename,
                        )
                    )
                )
        else:
            deleted_files_count += 1

    await send_photos(
        callback=callback,
        state=state,
        callback_data=callback_data,
        media=media,
        request_id=request.id,
        deleted_files_count=deleted_files_count,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "TR_reopen_repair_docs")
)
async def reopen_repair_documents(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    media: list[InputMediaDocument] = []
    deleted_files_count = 0
    request = get_technical_request_by_id(callback_data.request_id)

    for photo in request.repair_photos:
        if photo.document.filename != settings.stubname:
            if "_reopen_" in photo.document.filename:
                media.append(
                    InputMediaDocument(
                        media=BufferedInputFile(
                            file=await photo.document.read(),
                            filename=photo.document.filename,
                        )
                    )
                )
        else:
            deleted_files_count += 1

    await send_photos(
        callback=callback,
        state=state,
        callback_data=callback_data,
        media=media,
        request_id=request.id,
        deleted_files_count=deleted_files_count,
    )
