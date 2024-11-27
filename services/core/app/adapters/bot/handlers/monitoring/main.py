from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hbold

from app.infra.database.models import IncidentStage
import app.services.equipment_status_service as es_service

import app.adapters.bot.kb as kb
from app.adapters.bot.handlers.utils import (
    try_edit_or_answer,
)
from app.adapters.bot.handlers.monitoring import utils
from app.adapters.bot.handlers.monitoring.schemas import (
    IncidentCallbackData,
    ConfirmIncidentCallbackData,
)


router = Router(name="personal_cabinet")


@router.callback_query(F.data == kb.get_monitoring_menu_btn.callback_data)
async def get_monitoring_menu(callback: CallbackQuery):
    await try_edit_or_answer(
        callback.message,
        text=hbold("Мониторинг инцидентов:"),
        reply_markup=kb.monitoring_menu,
    )


@router.callback_query(F.data == kb.get_monitoring_list_btn.callback_data)
async def get_monitoring_list(callback: CallbackQuery):
    await try_edit_or_answer(
        text=utils.get_monitoring_list(),
        message=callback.message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[kb.get_monitoring_menu_btn]]
        ),
    )


@router.callback_query(ConfirmIncidentCallbackData.filter())
async def confirm_incident(
    callback: CallbackQuery, callback_data: ConfirmIncidentCallbackData
):
    es_service.confirm_incident_by_id(callback_data.id)

    await get_incidents(callback)


@router.callback_query(IncidentCallbackData.filter())
async def get_incident(callback: CallbackQuery, callback_data: IncidentCallbackData):
    id = callback_data.id
    incident = es_service.get_incident_by_id(id)

    buttons: list[InlineKeyboardButton] = []

    if callback_data.with_confirm and incident.stage == IncidentStage.created:
        buttons.append(
            InlineKeyboardButton(
                text="Обработать",
                callback_data=ConfirmIncidentCallbackData(id=id).pack(),
            )
        )

    buttons.append(
        InlineKeyboardButton(text="Назад", callback_data=callback_data.callback_from)
    )

    await try_edit_or_answer(
        text=utils.get_incident_full_info(incident),
        message=callback.message,
        reply_markup=kb.create_inline_keyboard(*buttons),
    )


@router.callback_query(F.data == kb.get_incident_history_btn.callback_data)
async def get_incident_history(callback: CallbackQuery):
    incidents = es_service.get_incidents_history()
    incidents.sort(key=lambda incident: incident.id, reverse=True)
    incidents = incidents[:10]

    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text=utils.get_incident_short_info(incident),
            callback_data=IncidentCallbackData(
                id=incident.id,
                with_confirm=False,
                callback_from=kb.get_incident_history_btn.callback_data,
            ).pack(),
        )
        for incident in incidents
    ]
    keyboard = kb.create_inline_keyboard(*buttons, kb.get_monitoring_menu_btn)

    await try_edit_or_answer(
        text="История инцидентов",
        message=callback.message,
        reply_markup=keyboard,
    )


@router.callback_query(F.data == kb.get_incidents_btn.callback_data)
async def get_incidents(callback: CallbackQuery):
    incidents = es_service.get_pending_incidents()
    incidents.sort(key=lambda incident: incident.id)
    incidents = incidents[:10]

    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text=utils.get_incident_short_info(incident),
            callback_data=IncidentCallbackData(
                id=incident.id,
                with_confirm=True,
                callback_from=kb.get_incidents_btn.callback_data,
            ).pack(),
        )
        for incident in incidents
    ]
    keyboard = kb.create_inline_keyboard(*buttons, kb.get_monitoring_menu_btn)

    await try_edit_or_answer(
        text="История инцидентов",
        message=callback.message,
        reply_markup=keyboard,
    )
