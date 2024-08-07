from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
)

# from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

# from fastapi import UploadFile

# from bot import text
# from bot.states import (
#     Base,
#     RepairmanTechnicalRequestForm,
#     WorkerTechnicalRequestForm,
# )
from bot.kb import (
    territorial_manager_tech_req_menu_button,
    territorial_manager_tech_req_menu,
    territorial_manager_tech_req_waiting,
    territorial_manager_tech_req_history,
)
from bot.handlers.utils import (
    try_edit_or_answer,
)
# from bot.handlers.tech_req.utils import (
#     create_keybord_with_end_point,
#     send_photos,
#     show_form,
# )
# from bot.handlers.tech_req.schemas import ShowRequestCallbackData

# from db.service import (
#     get_technical_problem_names,
#     create_technical_request,
#     get_technical_request_by_id,
#     update_technical_request_repairman,
# )

router = Router(name="technical_request_territorial_manager")


@router.callback_query(F.data == territorial_manager_tech_req_menu_button.callback_data)
async def territorial_manager_menu(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=territorial_manager_tech_req_menu,
    )


@router.callback_query(F.data == territorial_manager_tech_req_history.callback_data)
async def territorial_manager_history(callback: CallbackQuery):
    pass


@router.callback_query(F.data == territorial_manager_tech_req_waiting.callback_data)
async def territorial_manager_waiting(callback: CallbackQuery):
    pass
