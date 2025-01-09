from aiogram.utils.markdown import hbold

err = "Упс, произошла ошибка. Сейчас вы будете перенаправлены в главное меню."


def first_run_text(fullname: str) -> str:
    return (
        hbold(f"Добро пожаловать, {fullname}!")
        + "\n\n"
        + "Перед тем как начать, введите ваш рабочий номер телефона:"
    )


user_not_exist_text = (
    "Извините, но такого номера нет в базе данных.\n"
    + "Пожалуйста, обратитесь к вашему администратору."
)


# Bid
payment_types = ["cash", "card", "taxi"]

# description for bid settings menu
bid_create_greet = "Заполните вашу заявку:"


format_err = "Введен не верный формат.\nПожалуйста, введите верный:"

unclosed_shift_notify = "У вас осталась не закрытая смена!"
unclosed_shift_request = "Закройте смену!"

back = "⏪ Назад"


notification_repairman = "У Вас новая техническая заявка!"
notification_repairman_reopen = "У Вас новая техническая заявка на доработку!"

notification_territorial_manager_TR = "У Вас новая техническая заявка для оценки!"

notification_worker_TR = "Статус технической заявки обновлён!"

notification_it_worker = "Статус IT заявки обновлён!"
notification_it_territorial_manager = "У Вас новая IT заявка для оценки!"
notification_it_repairman = "У Вас новая IT заявка!"
notification_it_repairman_reopen = "У Вас новая IT заявка на доработку!"

personal_cabinet_logins_dict = {
    "cop_mail_login": "Корпоративная почта",
    "liko_login": "Iiko",
    "bitrix_login": "Bitrix",
    "pyrus_login": "Pyrus",
    "check_office_login": "CheckOffice",
    "pbi_login": "PBI",
}


problem_groups = ["Техническая", "Клининговая"]
problem_groups_dict = {"Техническая": "TR", "Клининговая": "CR"}


notification_cleaner = "У Вас новая заявка на клининг!"
notification_cleaner_reopen = "У Вас новая заявка на доработку по клинингу!"

notification_territorial_manager_CR = "У Вас новая заявка для оценки клининга!"

notification_worker_CR = "Статус заявки в клининг обновлён!"
