from aiogram import Router, F

from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from fastapi import UploadFile

from bot import text
from bot.states import (
    Base,
    RepairmanTechnicalRequestForm,
)
from bot.kb import (
    create_reply_keyboard,
    repairman_tech_req_button,
    repairman_tech_req_menu_markup,
    repairman_tech_req_menu_button,
    repairman_tech_req_change_department_button,
    repairman_tech_req_change_deparment_menu,
    repairman_tech_req_waiting,
    repairman_repair_tech_req_kb,
    repairman_tech_req_history,
)
from bot.handlers.utils import (
    notify_worker_by_telegram_id,
    try_edit_or_answer,
    try_delete_message,
    download_file,
    handle_documents_form,
    handle_documents,
)
from bot.handlers.tech_req.utils import (
    create_keybord_for_requests_with_end_point,
    show_form,
)
from bot.handlers.tech_req.schemas import ShowRequestCallbackData

from db.service import (
    get_all_history_technical_requests_by_repairman_TG_id_and_department_name,
    get_all_waiting_technical_requests_by_repairman_TG_id_and_department_name,
    get_deparments_by_repairman_telegram_id,
    update_technical_request_from_repairman,
)

router = Router(name="technical_request_repairman")


@router.callback_query(F.data == repairman_tech_req_button.callback_data)
async def repairman_menu_cb(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=repairman_tech_req_change_deparment_menu,
    )


async def repairman_menu_ms(message: Message):
    await message.answer(
        text=hbold("Тех. заявки"),
        reply_markup=repairman_tech_req_change_deparment_menu,
    )


@router.callback_query(
    F.data == repairman_tech_req_change_department_button.callback_data
)
async def department_change(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RepairmanTechnicalRequestForm.department)
    departments = get_deparments_by_repairman_telegram_id(callback.message.chat.id)

    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите производство:"),
        reply_markup=create_reply_keyboard(
            "⏪ Назад", *[department.name for department in departments]
        ),
    )
    await state.update_data(msg=msg)


@router.message(RepairmanTechnicalRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == "⏪ Назад":
        await repairman_menu_ms(message)
    else:
        deparment_names = [
            department.name
            for department in get_deparments_by_repairman_telegram_id(message.chat.id)
        ]
        if message.text not in deparment_names:
            deparment_names.sort()
            msg = await message.answer(
                text=text.format_err,
                reply_markup=create_reply_keyboard(
                    *[department for department in deparment_names]
                ),
            )
            await state.update_data(msg=msg)
            return
        await state.update_data(department_name=message.text)
        await message.answer(
            text=hbold(f"Производство: {message.text}"),
            reply_markup=repairman_tech_req_menu_markup,
        )


@router.callback_query(F.data == repairman_tech_req_menu_button.callback_data)
async def repairman_manager_tech_req_menu_button(
    callback: CallbackQuery, state: FSMContext
):
    department_name = (await state.get_data()).get("department_name")
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Производство: {department_name}"),
        reply_markup=repairman_tech_req_menu_markup,
    )


@router.callback_query(F.data == repairman_tech_req_history.callback_data)
async def repairman_history(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = (
        get_all_history_technical_requests_by_repairman_TG_id_and_department_name(
            telegram_id=callback.message.chat.id, department_name=department_name
        )
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("История заявок"),
        reply_markup=create_keybord_for_requests_with_end_point(
            end_point="repairman_show_form_history",
            menu_button=repairman_tech_req_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "repairman_show_form_history")
)
async def repairman_show_form_history(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = []
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_button=repairman_tech_req_history,
    )


@router.callback_query(F.data == repairman_tech_req_waiting.callback_data)
async def repairman_waiting(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = (
        get_all_waiting_technical_requests_by_repairman_TG_id_and_department_name(
            telegram_id=callback.message.chat.id, department_name=department_name
        )
    )
    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Ожидающие заявки"),
        reply_markup=create_keybord_for_requests_with_end_point(
            end_point="repairman_show_form_waiting",
            menu_button=repairman_tech_req_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "repairman_show_form_waiting")
)
async def repairman_show_form_waiting(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Выполнить заявку",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="repairman_repair_form",
                ).pack(),
            )
        ]
    ]
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_button=repairman_tech_req_waiting,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "repairman_repair_form")
)
async def repairman_repair_form_cb(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Выполнить заявку"),
        reply_markup=await repairman_repair_tech_req_kb(
            state=state, callback_data=callback_data
        ),
    )


async def repairman_repair_form_ms(message: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Выполнить заявку"),
        reply_markup=await repairman_repair_tech_req_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="repairman_repair_form",
            ),
        ),
    )


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "get_photo"))
async def get_repairman_photo(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.update_data(request_id=callback_data.request_id)
    await handle_documents_form(
        callback.message, state, RepairmanTechnicalRequestForm.photo
    )


@router.message(RepairmanTechnicalRequestForm.photo)
async def set_repairman_photo(message: Message, state: FSMContext):
    await handle_documents(message, state, "photo", repairman_repair_form_ms)


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "save_repairman_repair")
)
async def save_repairman_repair(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    data = await state.get_data()

    photo = data["photo"]
    photo_files: list[UploadFile] = []
    for doc in photo:
        photo_files.append(await download_file(doc))

    req_data = update_technical_request_from_repairman(
        photo_files=photo_files, request_id=callback_data.request_id
    )

    await notify_worker_by_telegram_id(
        id=req_data["territorial_manager_telegram_id"],
        message=text.notifay_teritorial_manager
        + f"\n На производстве: {req_data["department_name"]}",
    )

    await state.clear()
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=repairman_tech_req_change_deparment_menu,
    )
