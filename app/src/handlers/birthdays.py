from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter
from src.bases.db_operations import BirthdayOperation
from create_bot import dp

#Реагируем на команду с днями рождения
async def mybirthday_message(message:types.Message):
    '''
    Выводит или изменяет день рождения пользователя
    '''
    user_message = message.text[12:]

    #Отрезаем имя бота, если команда выбрана из списка
    if user_message == 'ZoroasterOfTomskBot': user_message = ''

    #Получаем день рождения пользователя из базы
    user_birthday = BirthdayOperation(message)
    user_birthday.get_user_birthday(user_message)

    if user_message != '':
        if user_birthday.validation_birthday['status'] != False:
            if user_birthday.user_birthday != None:
                user_birthday.update_user_birthday()
            else:
                user_birthday.add_user_birthday()
            await message.reply('День рождения записан!')
        else:
            await message.reply('Неправильный формат дня рождения.')
    elif user_birthday.user_birthday != None and user_message == '':
        await message.reply(f"У тебя зарегистрирован день рождения {user_birthday.full_birthday}.")
    else:
        await message.reply('У тебя не зарегистрирован день рождения. Набери "/mybirthday <ДДММ>". '
        'Например, для 11 сентября будет /mybirthday 1109.')

#Выводим список дней рождения
async def allbirthday_message(message:types.Message):
    '''
    Выводит список всех дней рождения
    '''
    chat_birthdays = BirthdayOperation(message).get_all_birthday()

    if chat_birthdays != []:
        birthday_list = ['Дни рождения всех уважаемых членов группы:'] + chat_birthdays
        birthday_message = '\n'.join(birthday_list)
        await message.reply(birthday_message)
    else:
        await message.reply('В чате не зарегистрированы дни рождения.')

def register_handlers_birthdays(dp:Dispatcher):
    dp.register_message_handler(mybirthday_message, ChatTypeFilter(chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP]), commands=['mybirthday'])
    dp.register_message_handler(allbirthday_message, ChatTypeFilter(chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP]), commands=['allbirthday'])