from pathlib import Path
from sqlalchemy import null
from datetime import datetime, timedelta
from fastapi import UploadFile
from typing import Any, Optional

from app.infra.logging import logger

import app.infra.database.orm as orm
from app.infra.database.models import (
    Department,
    ApprovalStatus,
    TechnicalRequest,
    CleaningRequest,
    Worker,
    FujiScope,
)
from app.schemas import (
    TechnicalProblemSchema,
    TechnicalRequestSchema,
    WorkerSchema,
    DocumentSchema,
)
from app.adapters.bot.handlers.department_request.schemas import (
    ShowRequestCallbackData,
    RequestType,
)


async def notify_worker_by_telegram_id_in_technical_request(
    telegram_id, message: str, request_id: int, end_point: str
):
    from app.adapters.bot.kb import create_inline_keyboard
    from app.adapters.bot.handlers.utils import notify_worker_by_telegram_id
    from app.adapters.bot import text
    from aiogram.types import InlineKeyboardButton

    await notify_worker_by_telegram_id(
        id=telegram_id,
        message=message,
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text=text.view,
                callback_data=ShowRequestCallbackData(
                    request_id=request_id,
                    end_point=end_point,
                    req_type=RequestType.TR.value,
                ).pack(),
            )
        ),
    )


def counting_date_sla(sla: int):
    deadline_date = datetime.now()
    start_work_day = 9
    end_work_day = 18

    if deadline_date.hour >= end_work_day:
        deadline_date = deadline_date.replace(hour=start_work_day + 1)
        deadline_date += timedelta(days=1)
    elif deadline_date.hour <= start_work_day:
        deadline_date = deadline_date.replace(hour=start_work_day + 1)

    weekday = deadline_date.weekday()
    if weekday > 4:  # 0 - понедельник, 6 - воскресенье
        deadline_date += timedelta(days=(7 - weekday))

    while sla > 8:
        deadline_date += timedelta(days=1)
        sla -= 9

        weekday = deadline_date.weekday()
        if weekday > 4:  # 0 - понедельник, 6 - воскресенье
            deadline_date += timedelta(days=(7 - weekday))

    deadline_date += timedelta(hours=sla)
    return deadline_date


def get_technical_request_by_id(request_id: int) -> TechnicalRequestSchema:
    """
    Return TechnicalRequestSchema by id
    """
    try:
        request = orm.get_technical_requests_by_column(TechnicalRequest.id, request_id)[
            0
        ]
        return request
    except IndexError:
        logger.error(f"Request with id: {request_id} wasn't founds")


def get_technical_problem_names() -> list[str]:
    return [problem.problem_name for problem in orm.get_technical_problems()]


def get_technical_problems() -> list[TechnicalProblemSchema]:
    return [problem for problem in orm.get_technical_problems()]


def get_technical_problem_by_name(problem_name) -> TechnicalProblemSchema:
    return orm.get_technical_problem_by_name(problem_name=problem_name)


def get_technical_problem_by_id(problem_id) -> TechnicalProblemSchema:
    return orm.get_technical_problem_by_id(problem_id=problem_id)


async def create_technical_request(
    problem_name: str,
    description: str,
    photo_files: list[UploadFile],
    telegram_id: int,
    department_name: str,
) -> bool:
    from app.adapters.bot import text

    """
    Create technical request
    Return: bool
    """
    cur_date = datetime.now()

    last_technical_request_id = orm.get_last_technical_request_id()
    if not last_technical_request_id:
        last_technical_request_id = 0

    department = orm.find_departments_by_name(department_name)
    if len(department) == 0:
        logger.error(f"Department with name: {department_name} wasn't found")
    department = department[0]

    worker = orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    if not worker:
        logger.error(f"Worker with telegram id {telegram_id} wasn't found")

    problem = orm.get_technical_problem_by_problem_name(problem_name=problem_name)
    if not problem:
        logger.error(f"Problem with name {problem_name} wasn't found")

    repairman = orm.get_repairman_by_department_id_and_executor_type(
        department_id=department.id, executor_type=problem.executor.name
    )

    if not repairman:
        logger.error(
            f"Repairman from department id: {department.id} and responsible by {problem.executor.name} wasn't found"
        )
    appraiser = orm.get_restaurant_manager_by_department_id(department.id)
    if appraiser is None:
        appraiser = orm.get_territorial_manager_by_department_id(department.id)
        if appraiser is None:
            logger.error(
                f"Territorial manager with department id: {department.id} wasn't found"
            )

    documents = []
    for index, doc in enumerate(photo_files):
        suffix = Path(doc.filename).suffix
        filename = f"photo_problem_technical_request_{last_technical_request_id + 1}_{index + 1}{suffix}"
        doc.filename = filename
        documents.append(DocumentSchema(document=doc))

    deadline_date = counting_date_sla(problem.sla)

    request = TechnicalRequestSchema(
        problem=problem,
        description=description,
        problem_photos=documents,
        state=ApprovalStatus.pending,
        open_date=cur_date,
        deadline_date=deadline_date,
        worker=worker,
        repairman=repairman,
        appraiser=appraiser,
        department=department,
        repairman_worktime=0,
    )

    if not orm.create_technical_request(request):
        logger.error("Technical request record wasn't created")
        return False
    else:
        chief_technician = orm.get_chief_technician(request.department.id)
        if chief_technician is None:
            logger.error(
                f"The chief technician wasn't found at department {request.department.id}"
            )
        else:
            await notify_worker_by_telegram_id_in_technical_request(
                telegram_id=chief_technician.telegram_id,
                message=f"Заявка с номером {last_technical_request_id + 1} передана в исполнение.\nПредприятие: {request.department.name}",
                request_id=last_technical_request_id + 1,
                end_point="show_CT_TR_admin_form",
            )

        extensive_directors = orm.get_workers_with_scope(
            FujiScope.bot_technical_request_extensive_director
        )
        if extensive_directors == []:
            logger.error(
                f"The Directors of Extensive Development wasn't found at department {request.department.id}"
            )
        else:
            for extensive_director in extensive_directors:
                await notify_worker_by_telegram_id_in_technical_request(
                    telegram_id=extensive_director.telegram_id,
                    message=f"Заявка с номером {last_technical_request_id + 1} передана в исполнение.\nПредприятие: {request.department.name}",
                    request_id=last_technical_request_id + 1,
                    end_point="ED_TR_show_form_active",
                )
        await notify_worker_by_telegram_id_in_technical_request(
            telegram_id=request.repairman.telegram_id,
            message=text.notification_repairman
            + f"\nНомер заявки: {last_technical_request_id + 1}\nНа предприятии: {request.department.name}",
            request_id=last_technical_request_id + 1,
            end_point=f"{RequestType.TR.name}_show_waiting_form",
        )
    return True


async def update_technical_request_from_repairman(
    photo_files: list[UploadFile], request_id: int
) -> bool:
    from app.adapters.bot import text

    """
    Update technical request
    Notifies appraiser, chief technician and request of the request
    """
    cur_date = datetime.now()

    request: TechnicalRequestSchema = get_technical_request_by_id(request_id=request_id)
    if request.state != ApprovalStatus.pending:
        return False

    if request.reopen_date:
        request.reopen_repair_date = cur_date
        for index, doc in enumerate(photo_files):
            suffix = Path(doc.filename).suffix
            filename = f"photo_repair_technical_request_{request_id}_reopen_{index + 1}{suffix}"
            doc.filename = filename
            request.repair_photos.append(DocumentSchema(document=doc))
        if request.reopen_date.date() == cur_date.date():
            request.repairman_worktime += (
                cur_date.hour - request.reopen_date.hour
            )  # until work day
        else:
            request.repairman_worktime += cur_date.hour - 9

    else:
        request.repair_date = cur_date
        if request.open_date.date() == cur_date.date():
            request.repairman_worktime = cur_date.hour - max(request.open_date.hour, 9)
        documents = []
        for index, doc in enumerate(photo_files):
            suffix = Path(doc.filename).suffix
            filename = (
                f"photo_repair_technical_request_{request_id}_{index + 1}{suffix}"
            )
            doc.filename = filename
            documents.append(DocumentSchema(document=doc))

        request.repair_photos = documents

    request.state = ApprovalStatus.pending_approval

    if not orm.update_technical_request_from_repairman(request):
        logger.error(f"Technical problem with id {request.id} record wasn't updated")
        return False
    else:
        await notify_worker_by_telegram_id_in_technical_request(
            telegram_id=request.appraiser.telegram_id,
            message=text.notification_appraiser_TR
            + f"\nНомер заявки: {request_id}\nНа предприятии: {request.department.name}",
            request_id=request_id,
            end_point=f"{RequestType.TR.name}_show_waiting_form_AR",
        )
        await notify_worker_by_telegram_id_in_technical_request(
            telegram_id=request.worker.telegram_id,
            message=text.notification_worker_TR
            + f"\nЗаявка {request_id} на проверке ТУ.",
            request_id=request_id,
            end_point="WR_DR_show_form_waiting",
        )

        chief_technician = orm.get_chief_technician(request.department.id)
        if chief_technician is None:
            logger.error(
                f"The chief technician wasn't found at department {request.department.id}"
            )
        else:
            await notify_worker_by_telegram_id_in_technical_request(
                telegram_id=chief_technician.telegram_id,
                message=f"Заявка с номером {request_id} на проверке ТУ.\nПредприятие: {request.department.name}",
                request_id=request_id,
                end_point="show_CT_TR_admin_form",
            )

        extensive_directors = orm.get_workers_with_scope(
            FujiScope.bot_technical_request_extensive_director
        )
        if extensive_directors == []:
            logger.error(
                f"The Director of Extensive Development wasn't found at department {request.department.id}"
            )
        else:
            for extensive_director in extensive_directors:
                await notify_worker_by_telegram_id_in_technical_request(
                    telegram_id=extensive_director.telegram_id,
                    message=f"Заявка с номером {request_id} на проверке ТУ.\nПредприятие: {request.department.name}",
                    request_id=request_id,
                    end_point="ED_TR_show_form_active",
                )

    return True


async def update_technical_request_from_appraiser(
    mark: int, request_id: int, description: Optional[str]
) -> bool:
    from app.adapters.bot import text

    """
    Update technical request
    Return repairman telegram id if mark == 1 else None
    """
    cur_date = datetime.now()

    request = get_technical_request_by_id(request_id=request_id)
    if request.state != ApprovalStatus.pending_approval:
        return False
    request.score = mark

    if request.reopen_date:
        request.close_description = description
    else:
        request.confirmation_description = description

    if mark != 1:
        request.state = ApprovalStatus.approved
        request.close_date = cur_date
        request.acceptor_post = request.appraiser.post
        if request.reopen_date:
            request.reopen_confirmation_date = cur_date
        else:
            request.confirmation_date = cur_date
    else:
        if request.reopen_date:
            request.state = ApprovalStatus.skipped
            request.close_date = cur_date
            request.reopen_confirmation_date = cur_date
        else:
            request.state = ApprovalStatus.pending
            request.confirmation_date = cur_date
            request.reopen_date = cur_date
            if request.repairman_worktime > 0:
                if cur_date.hour >= 18:  # end_work_day
                    request.repairman_worktime -= 9
                elif cur_date.hour >= 9:  # start_work_day
                    request.repairman_worktime -= cur_date.hour - 9
            request.reopen_deadline_date = counting_date_sla(24)

    if not orm.update_technical_request_from_appraiser(request):
        logger.error(f"Technical problem with id {request.id} record wasn't updated")
        return False
    else:
        if mark == 1 and request.state == ApprovalStatus.pending:
            await notify_worker_by_telegram_id_in_technical_request(
                telegram_id=request.repairman.telegram_id,
                message=text.notification_repairman_reopen
                + f"\nНомер заявки: {request_id}\nНа предприятии: {request.department.name}",
                request_id=request_id,
                end_point=f"{RequestType.TR.name}_show_rework_form",
            )

            chief_technician = orm.get_chief_technician(request.department.id)
            if chief_technician is None:
                logger.error(
                    f"The chief technician wasn't found at department {request.department.id}"
                )
            else:
                await notify_worker_by_telegram_id_in_technical_request(
                    telegram_id=chief_technician.telegram_id,
                    message=f"Заявка с номером {request_id} отправлена на доработку.\nПредприятие: {request.department.name}",
                    request_id=request_id,
                    end_point="show_CT_TR_admin_form",
                )

            extensive_directors = orm.get_workers_with_scope(
                FujiScope.bot_technical_request_extensive_director
            )
            if extensive_directors == []:
                logger.error(
                    f"The Director of Extensive Development wasn't found at department {request.department.id}"
                )
            else:
                for extensive_director in extensive_directors:
                    await notify_worker_by_telegram_id_in_technical_request(
                        telegram_id=extensive_director.telegram_id,
                        message=f"Заявка с номером {request_id} отправлена на доработку.\nПредприятие: {request.department.name}",
                        request_id=request_id,
                        end_point="ED_TR_show_form_active",
                    )
            await notify_worker_by_telegram_id_in_technical_request(
                telegram_id=request.worker.telegram_id,
                message=text.notification_worker_TR
                + f"\nЗаявка {request_id} отправлена на доработку.",
                request_id=request_id,
                end_point="WR_DR_show_form_waiting",
            )
        else:
            await notify_worker_by_telegram_id_in_technical_request(
                telegram_id=request.worker.telegram_id,
                message=text.notification_worker_TR + f"\nЗаявка {request_id} закрыта.",
                request_id=request_id,
                end_point="WR_DR_show_form_waiting",
            )
    return True


def get_active_state_by_columns(request: TechnicalRequestSchema):
    for key, val in {
        "repair_date": ApprovalStatus.pending,
        "confirmation_date": ApprovalStatus.pending_approval,
        "reopen_repair_date": ApprovalStatus.pending,
        "reopen_confirmation_date": ApprovalStatus.pending_approval,
    }.items():
        if getattr(request, key) is None:
            return val
    return ApprovalStatus.skipped if request.score == 1 else ApprovalStatus.approved


async def update_technical_request_by_territorial_director(
    id: int,
    correct_option: bool,
    description: str,
) -> bool:
    request = orm.get_technical_requests_by_column(
        column=TechnicalRequest.id,
        value=id,
    )
    if request == []:
        logger.error(f"Technical request with id: {id} wasn't found")
    request = request[0]

    request.not_relevant_confirmation_description = description
    request.not_relevant_confirmation_date = datetime.now()

    if correct_option:
        request.close_date = datetime.now()
        request.close_description = description
        if not orm.update_technical_request_from_territorial_director(request=request):
            logger.error(
                f"Technical request with id {request.id} wasn't update by department director"
            )
            return False

        message = f"Техническая заявка с номером {request.id} закрыта как не релевантная.\nПроизводство: {request.department.name}"

        await notify_worker_by_telegram_id_in_technical_request(
            telegram_id=request.worker.telegram_id,
            message=message,
            request_id=request.id,
            end_point="WR_TR_show_form_history",
        )

        chief_technician = orm.get_chief_technician(request.department.id)
        if chief_technician is None:
            logger.error(
                f"Chief technician in department with id: {request.department.id} wasn't found"
            )
        else:
            await notify_worker_by_telegram_id_in_technical_request(
                telegram_id=chief_technician.telegram_id,
                message=message,
                request_id=request.id,
                end_point="show_CT_TR_admin_form",
            )

        extensive_directors = orm.get_workers_with_scope(
            FujiScope.bot_technical_request_extensive_director
        )
        for extensive_director in extensive_directors:
            if extensive_director is None:
                logger.error("Extensive directors weren't found")
            else:
                await notify_worker_by_telegram_id_in_technical_request(
                    telegram_id=extensive_director.telegram_id,
                    message=message,
                    request_id=request.id,
                    end_point="ED_TR_show_form_history",
                )
    else:
        request.state = get_active_state_by_columns(request=request)
        if not orm.update_technical_request_from_territorial_director(request=request):
            logger.error(
                f"Technical request with id {request.id} wasn't update by department director"
            )
            return False

        if request.state == ApprovalStatus.pending:
            message = f"Техническая заявка с номером {request.id} восстановлена и ожидает выполнения"

            await notify_worker_by_telegram_id_in_technical_request(
                telegram_id=request.repairman.telegram_id,
                message=message,
                request_id=request.id,
                end_point="RM_TR_show_form_rework"
                if request.reopen_repair_date is None
                else "RM_TR_repair_waiting_form",
            )

        elif request.state == ApprovalStatus.pending_approval:
            message = f"Техническая заявка с номером {request.id} восстановлена и ожидает оценки"
            await notify_worker_by_telegram_id_in_technical_request(
                telegram_id=request.appraiser.telegram_id,
                message=message,
                request_id=request.id,
                end_point="AR_TR_show_form_waiting",
            )
        else:
            message = f"Техническая заявка с номером {request.id} закрыта"
            logger.error(
                f"Executor for technical request with id {request.id} for stage {request.state} wasn't found"
            )
        message += f"\nПроизводство: {request.department.name}"
        await notify_worker_by_telegram_id_in_technical_request(
            telegram_id=request.worker.telegram_id,
            message=message,
            request_id=request.id,
            end_point="WR_TR_show_form_history",
        )

        chief_technician = orm.get_chief_technician(request.department.id)
        if chief_technician is None:
            logger.error(
                f"Chief technician in department with id: {request.department.id} wasn't found"
            )
        else:
            await notify_worker_by_telegram_id_in_technical_request(
                telegram_id=chief_technician.telegram_id,
                message=message,
                request_id=request.id,
                end_point="show_CT_TR_admin_form",
            )

        extensive_directors = orm.get_workers_with_scope(
            FujiScope.bot_technical_request_extensive_director
        )
        for extensive_director in extensive_directors:
            if extensive_director is None:
                logger.error("Extensive directors weren't found")
            else:
                await notify_worker_by_telegram_id_in_technical_request(
                    telegram_id=extensive_director.telegram_id,
                    message=message,
                    request_id=request.id,
                    end_point="ED_TR_show_form_active",
                )

    return True


async def update_tech_request_executor(
    request_id: int, repairman_full_name: list[str], department_name: str
) -> int:
    """
    Update executor in technical request return telegram id
    """
    try:
        new_repairman = orm.get_workers_with_post_by_columns(
            [Worker.l_name, Worker.f_name, Worker.o_name], repairman_full_name
        )[0]
    except IndexError:
        logger.error(f"Worker with full name: {repairman_full_name} wasn't found")

    if not orm.update_tech_request_executor(
        request_id=request_id, repairman_id=new_repairman.id
    ):
        logger.error(f"Technical request with id: {request_id} wasn't update executor")
        return False
    await notify_worker_by_telegram_id_in_technical_request(
        telegram_id=new_repairman.telegram_id,
        message=f"Вас назначили на заявку {request_id}\nНа предприятие: {department_name}",
        request_id=request_id,
        end_point="RM_TR_repair_waiting_form",
    )
    return True


def update_technical_request_problem(request_id: int, problem_id: int):
    if not orm.update_technical_request_problem(
        request_id=request_id, problem_id=problem_id
    ):
        logger.error(f"Technical request with id: {request_id} wasn't update problem")


def get_all_waiting_technical_requests_for_worker(
    telegram_id: int, limit: int = 15
) -> list[TechnicalRequestSchema]:
    """
    Return all technical requests by Telegram id
    """
    try:
        worker = orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    except IndexError:
        logger.error(f"Worker with telegram id {telegram_id} wasn't found")
    else:
        requests = orm.get_technical_requests_by_columns(
            columns=[TechnicalRequest.worker_id, TechnicalRequest.close_date],
            values=[worker.id, null()],
            limit=limit,
        )

    return requests


def get_all_waiting_technical_requests_for_repairman(
    telegram_id: int, department_name: str, limit: int = 15
) -> list[TechnicalRequestSchema]:
    """
    Return all waiting technical requests by Telegram id for repairman
    """
    try:
        repairman = orm.get_workers_with_post_by_column(
            Worker.telegram_id, telegram_id
        )[0]
    except IndexError:
        logger.error(f"Repairman with telegram id: {telegram_id} wasn't found")
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logger.error(f"Department with name: {department_name} wasn't found")
        else:
            requests = orm.get_technical_requests_by_columns(
                columns=[
                    TechnicalRequest.repairman_id,
                    TechnicalRequest.state,
                    TechnicalRequest.department_id,
                    TechnicalRequest.confirmation_date,
                ],
                values=[repairman.id, ApprovalStatus.pending, department_id, null()],
                limit=limit,
            )

        return requests


def get_all_active_technical_requests_for_extensive_director(
    department_name: str, limit: int = 15
) -> list[TechnicalRequestSchema]:
    """
    Return all waiting technical requests by Telegram id for extensive_director
    """
    try:
        department = orm.find_departments_by_name(department_name)[0]
    except IndexError:
        logger.error(f"Department with name {department_name} wasn't found")
    else:
        requests = orm.get_all_technical_requests_in_department(
            department_id=department.id,
            history_flag=False,
            limit=limit,
        )
        return requests


def get_all_pending_technical_requests_for_territorial_director(
    department_name: str,
):
    try:
        department_id = (orm.find_departments_by_name(department_name)[0]).id
    except IndexError:
        logger.error(f"Department with name: {department_name} wasn't found")
    else:
        requests = orm.get_technical_requests_by_columns(
            [
                TechnicalRequest.state,
                TechnicalRequest.department_id,
                TechnicalRequest.close_date,
            ],
            [
                ApprovalStatus.not_relevant,
                department_id,
                null(),
            ],
        )

        return requests


def get_all_rework_technical_requests_for_repairman(
    telegram_id: int,
    department_name: str,
) -> list[TechnicalRequestSchema]:
    """
    Return all waiting technical requests by Telegram id for repairman
    """
    try:
        repairman = orm.get_workers_with_post_by_column(
            Worker.telegram_id, telegram_id
        )[0]
    except IndexError:
        logger.error(f"Repairman with telegram id: {telegram_id} wasn't found")
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logger.error(f"Department with name: {department_name} wasn't found")
        else:
            requests = orm.get_rework_tech_request(
                department_id=department_id, repairman_id=repairman.id
            )[:-16:-1]
            return requests


def get_all_waiting_technical_requests_for_appraiser(
    telegram_id: int, department_name: str, limit: int = 15
) -> list[TechnicalRequestSchema]:
    """
    Return all waiting technical requests by Telegram id for appraiser
    """
    try:
        appraiser = orm.get_workers_with_post_by_column(
            Worker.telegram_id, telegram_id
        )[0]
    except IndexError:
        logger.error(f"Appraiser with telegram id: {telegram_id} wasn't found")
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logger.error(f"Department with name: {department_name} wasn't found")
        else:
            requests = orm.get_technical_requests_by_columns(
                columns=[
                    TechnicalRequest.appraiser_id,
                    TechnicalRequest.state,
                    TechnicalRequest.department_id,
                ],
                values=[
                    appraiser.id,
                    ApprovalStatus.pending_approval,
                    department_id,
                ],
                limit=limit,
            )

            return requests


def get_all_active_technical_requests_for_department_director(
    department_name: str, limit: int = 15
) -> list[TechnicalRequestSchema]:
    """
    Return all waiting technical requests by Telegram id for extensive_director
    """
    try:
        department = orm.find_departments_by_name(department_name)[0]
    except IndexError:
        logger.error(f"Department with name {department_name} wasn't found")
    else:
        requests = orm.get_all_technical_requests_in_department(
            department_id=department.id,
            history_flag=False,
            limit=limit,
        )
        return requests


def get_all_history_technical_requests_for_repairman(
    telegram_id: int, department_name: str, limit: int = 15
) -> list[TechnicalRequestSchema]:
    """
    Return all history technical requests by Telegram id for repairman
    """
    try:
        repairman = orm.get_workers_with_post_by_column(
            Worker.telegram_id, telegram_id
        )[0]
    except IndexError:
        logger.error(f"Repairman with telegram id: {telegram_id} wasn't found")
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logger.error(f"Department with name: {department_name} wasn't found")
        else:
            requests = orm.get_technical_requests_for_repairman_history(
                repairman.id, department_id, limit=limit
            )

            return requests


def get_all_history_technical_requests_for_appraiser(
    tg_id: int, department_name: str, limit: int = 15
) -> list[TechnicalRequestSchema]:
    """
    Return all history technical requests by Telegram id for appraiser
    """
    try:
        appraiser = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)[0]
    except IndexError:
        logger.error(f"Appraiser with telegram id: {tg_id} wasn't found")
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logger.error(f"Department with name: {department_name} wasn't found")
        else:
            requests = orm.get_technical_requests_by_columns(
                columns=[
                    TechnicalRequest.appraiser_id,
                    TechnicalRequest.department_id,
                ],
                values=[
                    appraiser.id,
                    department_id,
                ],
                history=True,
                limit=limit,
            )

            return requests


def get_all_history_technical_requests_for_worker(
    tg_id: int, limit: int = 15
) -> list[TechnicalRequestSchema]:
    """
    Return history technical requests by Telegram id for worker
    """
    try:
        worker = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)[0]
    except IndexError:
        logger.error(f"Worker with telegram id: {tg_id} wasn't found")
    else:
        requests = orm.get_technical_requests_by_columns(
            columns=[TechnicalRequest.worker_id],
            values=[worker.id],
            history=True,
            limit=limit,
        )

        return requests


def get_all_history_technical_requests_for_extensive_director(
    department_name: str, limit: int = 15
) -> list[TechnicalRequestSchema]:
    """
    Return history technical requests by Telegram id for worker
    """
    try:
        department = orm.find_departments_by_name(department_name)[0]
    except IndexError:
        logger.error(f"Department with name {department_name} wasn't found")
    else:
        requests = orm.get_all_technical_requests_in_department(
            department_id=department.id,
            history_flag=True,
            limit=limit,
        )

        return requests


def get_all_history_technical_requests_territorial_director(
    department_name: str,
):
    department = orm.find_departments_by_name(department_name)
    if department == []:
        logger.error(f"Department with name: {department_name} wasn't found")
        return []
    department = department[0]

    return orm.get_all_history_technical_requests_territorial_director(
        department_id=department.id
    )


def _get_departments_names_for_employee(
    telegram_id: int, worker_column: Any
) -> list[str]:
    """
    Return departments by worker telegram id and worker column id
    """
    try:
        worker = orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    except IndexError:
        logger.error(f"Worker with telegram id: {telegram_id} wasn't found")
    else:
        departments_names = orm.get_departments_names_by_worker_id_and_worker_column(
            worker_column=worker_column, worker_id=worker.id
        )
        return departments_names


def get_departments_names_for_repairman(
    telegram_id: int,
) -> list[str]:
    try:
        worker = orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    except IndexError:
        logger.error(f"Worker with telegram id: {telegram_id} wasn't found")
    else:
        return orm.get_departments_names_for_repairman(worker_id=worker.id)


def get_departments_names_for_appraiser(
    telegram_id: int,
) -> list[str]:
    return list(
        tuple(
            _get_departments_names_for_employee(
                telegram_id=telegram_id, worker_column=Department.territorial_manager_id
            )
            + _get_departments_names_for_employee(
                telegram_id=telegram_id, worker_column=Department.restaurant_manager_id
            )
        )
    )


def get_departments_names_for_territorial_director(
    telegram_id: int,
) -> list[str]:
    return _get_departments_names_for_employee(
        telegram_id=telegram_id, worker_column=Department.territorial_director_id
    )


def get_departments_names_for_chief_technician(
    telegram_id: int,
) -> list[str]:
    return _get_departments_names_for_employee(
        telegram_id=telegram_id, worker_column=Department.chief_technician_id
    )


def get_all_active_requests_in_department_for_chief_technician(
    department_name: str, limit: int = 15
) -> list[TechnicalRequestSchema]:
    """
    Return all request in department
    """
    try:
        department_id = (orm.find_departments_by_name(department_name)[0]).id
    except IndexError:
        logger.error(f"Department with name: {department_name} wasn't found")
    else:
        requests = orm.get_all_active_requests_in_department_for_chief_technician(
            department_id, limit
        )
        return requests


def get_all_worker_in_group(
    group_name: str,
) -> list[WorkerSchema]:
    """
    Return all workers in group
    """
    group = orm.get_group_by_name(group_name)
    if not group:
        logger.error(f"Group with name: {group_name} wasn't found")
    workers = orm.get_all_worker_in_group(group.id)
    if len(workers) == 0:
        logger.error(f"Workers with group id: {group.id} wasn't founds")
    return workers


async def set_not_relevant_state(
    request_id: int,
    description: str,
    telegram_id: int,
) -> bool:
    """
    Close request by acceptor_post
    Return creator TG id
    """
    cur_date = datetime.now()
    request = orm.get_technical_requests_by_column(TechnicalRequest.id, request_id)
    if request == []:
        logger.error(f"Technical request with id: {request_id} wasn't found")
        return False
    request = request[0]
    if request.state not in [ApprovalStatus.pending, ApprovalStatus.pending_approval]:
        return False

    request.not_relevant_description = description
    request.not_relevant_date = cur_date
    request.acceptor_post = (
        orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    ).post

    if not orm.set_not_relevant_state(
        request=request,
    ):
        logger.error(f"Technical request with id: {request_id} wasn't update")
        return False
    else:
        await notify_worker_by_telegram_id_in_technical_request(
            telegram_id=request.worker.telegram_id,
            message=f"Техническая заявка с номером {request_id} передана на проверку релевантности.\nПроизводство: {request.department.name}",
            request_id=request_id,
            end_point="WR_TR_show_form_history",
        )
        if request.state == ApprovalStatus.pending:
            await notify_worker_by_telegram_id_in_technical_request(
                telegram_id=request.repairman.telegram_id,
                message=f"Техническая заявка с номером {request_id} передана на проверку релевантности.\nПроизводство: {request.department.name}",
                request_id=request_id,
                end_point="RM_TR_show_form_history",
            )
        elif request.state == ApprovalStatus.pending_approval:
            await notify_worker_by_telegram_id_in_technical_request(
                telegram_id=request.appraiser.telegram_id,
                message=f"Техническая заявка с номером {request_id} передана на проверку релевантности.\nПроизводство: {request.department.name}",
                request_id=request_id,
                end_point="AR_TR_show_form_history",
            )
        else:
            logger.error(
                f"Responsible by state {request.state} for technical request with id: {request_id} wasn't found"
            )
        chief_technician = orm.get_chief_technician(department_id=request.department.id)
        if chief_technician is None:
            logger.error(
                f"Chief technician for technical request with id: {request_id} wasn't found"
            )
        else:
            await notify_worker_by_telegram_id_in_technical_request(
                telegram_id=chief_technician.telegram_id,
                message=f"Техническая заявка с номером {request_id} передана на проверку релевантности.\nПроизводство: {request.department.name}",
                request_id=request_id,
                end_point="show_CT_TR_admin_form",
            )
        extensive_directors = orm.get_workers_with_scope(
            FujiScope.bot_technical_request_extensive_director
        )
        for extensive_director in extensive_directors:
            if extensive_director.telegram_id is not None:
                await notify_worker_by_telegram_id_in_technical_request(
                    telegram_id=extensive_director.telegram_id,
                    message=f"Техническая заявка с номером {request_id} передана на проверку релевантности.\nПроизводство: {request.department.name}",
                    request_id=request_id,
                    end_point="ED_TR_show_form_active",
                )
        territorial_director = orm.get_territorial_director(request.department.id)
        if territorial_director is None:
            logger.error(
                f"Territorial director for technical request with id: {request_id} wasn't found"
            )
        else:
            await notify_worker_by_telegram_id_in_technical_request(
                telegram_id=territorial_director.telegram_id,
                message=f"У Вас новая техническая заявка на проверку.\nНомер заявки {request_id}.\nПроизводство: {request.department.name}",
                request_id=request_id,
                end_point="TD_TR_show_pending_form",
            )
    return True


def get_request_count_in_departments_by_tg_id(
    state: ApprovalStatus,
    tg_id: int,
    model: TechnicalRequest | CleaningRequest,
) -> list[tuple[str, int]]:
    worker_id = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)
    if len(worker_id) == 0:
        logger.error(f"Worker with telegram id: {tg_id} not found")
    else:
        worker_id = worker_id[0].id

    return orm.get_count_req_in_departments(
        state=state, worker_id=worker_id, model=model
    )


def get_request_count_in_departments(
    state: ApprovalStatus,
    department_names: list[str],
    model: TechnicalRequest | CleaningRequest,
) -> tuple[str, int]:
    if department_names == []:
        return []
    departments_id = orm.get_departments_id_by_names(department_names)
    return orm.get_count_req_in_departments(
        state=state, departments_id=departments_id, model=model
    )


def update_repairman_worktimes(start_work_day: int, end_work_day: int) -> None:
    requests = orm.get_technical_requests_by_column(
        TechnicalRequest.state, ApprovalStatus.pending
    )
    worktime = end_work_day - start_work_day
    for request in requests:
        if request.repairman_worktime is None:
            request.repairman_worktime = 0
        if request.repairman_worktime > 0:  # Заявка уже проверялась
            request.repairman_worktime += worktime
        else:
            if request.open_date.weekday() > 4:  # Заявка создана в выходной
                request.repairman_worktime += worktime
            elif (
                request.open_date.hour > end_work_day
            ):  # Заявка создана после рабочего времени
                if (
                    request.open_date.date() != datetime.now().date()
                ):  # Заявка создана не сегодня
                    request.repairman_worktime += worktime
            elif (
                request.open_date.hour < start_work_day
            ):  # Заявка создана до рабочего времени
                request.repairman_worktime += worktime
            else:  # Заявка создана в рабочее время
                request.repairman_worktime += worktime - (
                    request.open_date.hour - start_work_day
                )
    orm.update_technical_requests_worktime(requests)
