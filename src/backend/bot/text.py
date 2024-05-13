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
