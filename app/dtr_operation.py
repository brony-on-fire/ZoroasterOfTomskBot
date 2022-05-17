'''
Модуль предназначен для преобразования даты рождения
'''

from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, "ru_RU.UTF8")

def full_birthday(birthday):
    '''
    Преобразует день рождения в человекочитаемый вид
    '''
    birthday_template = "%d %B"
    birthday = birthday.strftime(birthday_template)

    return birthday

def birthday_validator(birthday):
    '''
    Проверяет, что пользователь отправил дату рождения в правильном формате
    '''
    result = {'status': None, 'date': None}

    if len(birthday) != 4:
        result['status'] = False
    try:
        date = datetime.strptime(birthday, "%d%m")
        result['status'] = True
        result['date'] = date
    except ValueError:
        result['status'] = False

    return result