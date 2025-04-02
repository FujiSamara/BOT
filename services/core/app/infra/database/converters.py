from app.infra.database.models import ApprovalStatus, WorkerStatus, FujiScope, Gender

approval_status_dict = {
    ApprovalStatus.approved: "Согласовано",
    ApprovalStatus.pending: "Ожидает поступления",
    ApprovalStatus.pending_approval: "Ожидает согласования",
    ApprovalStatus.denied: "Отклонено",
    ApprovalStatus.skipped: "Не требуется",
    ApprovalStatus.not_relevant: "Не релевантно",
}

approval_status_technical_request_dict = {
    ApprovalStatus.approved: "Выполнено",
    ApprovalStatus.pending: "Ожидает выполнения",
    ApprovalStatus.pending_approval: "Ожидает согласования",
    ApprovalStatus.denied: "Отклонено",
    ApprovalStatus.skipped: "Не требуется",
    ApprovalStatus.not_relevant: "Не релевантно",
}


scope_decode_dict = {
    FujiScope.admin: "Админ",
    # CRM
    FujiScope.crm_bid: "CRM платёжные заявки",
    FujiScope.crm_budget: "CRM бюджет",
    FujiScope.crm_expenditure: "CRM статьи",
    FujiScope.crm_fac_cc_bid: "CRM платёжные заявки ЦФО ЦЗ",
    FujiScope.crm_paralegal_bid: "CRM платёжные заявки ЮК",
    FujiScope.crm_my_bid: "CRM мои платёжные заявки",
    FujiScope.crm_archive_bid: "CRM платёжные заявки архив",
    FujiScope.crm_my_file: "CRM скачивание файлов",
    FujiScope.crm_bid_readonly: "CRM платёжные заявки просмотр",
    FujiScope.crm_worktime: "CRM Явки",
    FujiScope.crm_accountant_card_bid: "CRM платёжные заявки бухгалтерия безнал",
    # Knowledge base
    FujiScope.crm_product_read: "CRM продукт просмотр",
    FujiScope.crm_marketing_read: "CRM маркетинг просмотр",
    FujiScope.crm_staff_read: "CRM перснал просмотр",
    FujiScope.crm_purchases_read: "CRM закупки просмотр",
    FujiScope.crm_cd_read: "CRM ЦД просмотр",
    FujiScope.crm_control_read: "CRM контроль качества просмотр",
    FujiScope.crm_accounting_read: "CRM учет просмотр",
    FujiScope.crm_product_write: "CRM продукт редактирование",
    FujiScope.crm_marketing_write: "CRM маркетинг редактирование",
    FujiScope.crm_staff_write: "CRM персонал редактирование",
    FujiScope.crm_purchases_write: "CRM закупки редактирование",
    FujiScope.crm_cd_write: "CRM ЦД редактирование",
    FujiScope.crm_control_write: "CRM контроль качества редактирование",
    FujiScope.crm_accounting_write: "CRM учет редактирование",
    # BOT
    FujiScope.bot_bid_create: "Бот создание платёжной заявки",
    FujiScope.bot_bid_kru: "Бот КРУ платёжные заявки",
    FujiScope.bot_bid_owner: "Бот Директор платёжные заявки",
    FujiScope.bot_bid_teller_cash: "Бот выдача денежных средств",
    FujiScope.bot_bid_teller_card: "Бот выплата денежных средств",
    FujiScope.bot_bid_accountant_cash: "Бот бухгалтерия наличная оплата",
    FujiScope.bot_bid_accountant_card: "Бот бухгалтерия безналичная оплата",
    FujiScope.bot_rate: "Бот оценка сотрудников",
    FujiScope.bot_worker_bid: "Бот подача сотрудника на согласование",
    FujiScope.bot_technical_request_worker: "Бот подача технической заявки",
    FujiScope.bot_technical_request_repairman: "Бот технические заявки исполнитель",
    FujiScope.bot_technical_request_chief_technician: "Бот технические заявки главный техник",
    FujiScope.bot_technical_request_appraiser: "Бот технические заявки оценка",
    FujiScope.bot_technical_request_extensive_director: "Бот технические заявки ДЭР",
    FujiScope.bot_bid_it_worker: "Бот подача IT заявки",
    FujiScope.bot_bid_it_repairman: "Бот IT заявки исполнитель",
    FujiScope.bot_bid_it_tm: "Бот IT заявки ТУ",
    FujiScope.bot_personal_cabinet: "Бот личный кабинет",
    FujiScope.bot_incident_monitoring: "Бот мониторинг точек",
    FujiScope.bot_bid_fac_cc: "Бот платёжные заявки ЦФО ЦЗ",
    FujiScope.bot_subordinates_menu: "Бот меню сотрудники",
    FujiScope.bot_worker_bid_security_coordinate: "Бот согласование кандидатов СБ",
    FujiScope.bot_worker_bid_accounting_coordinate: "Бот согласование кандидатов бухгалтерия",
    FujiScope.bot_worker_bid_iiko: "Бот согласование кандидатов добавление в IIKO",
    FujiScope.bot_technical_request_department_director: "Бот технические заявки ТД",
    FujiScope.bot_change_restaurant_menu: "Бот обновление меню",
    FujiScope.bot_worker_bid_financial_director: "Бот согласование кандидатов финансовый директор",
}


worker_status_dict = {
    WorkerStatus.pending_approval: "На согласовании",
    WorkerStatus.internship: "На стажировке",
    WorkerStatus.refusal_internship: "Отказ от стажировки",
    WorkerStatus.active: "В штате",
    WorkerStatus.process_dismissal: "В процессе увольнения",
    WorkerStatus.dismissal: "Уволен",
}

gender_decode_dict = {
    Gender.man: "Мужской",
    Gender.woman: "Женский",
}
