from aiogram.utils.markdown import hbold


def first_run_text(fullname: str) -> str:
    return (hbold(f"Добро пожаловать, {fullname}!") + 
                         '\n\n'
                          + "Перед тем как начать, введите ваш рабочий номер телефона:")

user_not_exist_text = "Извините, но такого номера нет в базе данных.\nПожалуйста, обратитесь к вашему администратору."