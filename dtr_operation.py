'''
Модуль предназначен для преобразования даты рождения
'''
#/usr/bin/env python3

from time import strptime, strftime
import locale

locale.setlocale(locale.LC_TIME, "ru_RU.UTF8")

def full_birthday(birthday: str):
    birthday = strptime(birthday, "%d%m")
    birthday_template = "%d %B"
    birthday = strftime(birthday_template, birthday)

    return birthday