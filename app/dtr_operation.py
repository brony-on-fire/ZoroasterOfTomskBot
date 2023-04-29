'''
Модуль предназначен для преобразования даты рождения
'''
#/usr/bin/env python3

from time import strptime, strftime
from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, "ru_RU.UTF8")

def full_birthday(birthday: str):
    birthday = strptime(birthday, "%d%m")
    birthday_template = "%d %B"
    birthday = strftime(birthday_template, birthday)

    return birthday

def sorted_birthday(birthday_hash):
    '''
    Сортирует дни рождения по дате
    '''
    birthday_list = []

    #Создаем список для сортировки
    for key in birthday_hash:
        birthday_list.append([birthday_hash[key][2], birthday_hash[key][1]])

    #Сортируем список
    birthday_list = sorted(birthday_list, key=lambda d: datetime.strptime(d[0] + '1904', '%d%m%Y'))

    #Преобразуем даты в читаемый формат
    birthday_list = [f'{user_name} - {full_birthday(birthday)}' for birthday, user_name in birthday_list]

    return birthday_list