from aiogram import Bot, Dispatcher, executor, types
from os import environ
from random import randint
from typing import List
from time import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tables import engine_settings, Base, Word, Answer, User, Birthday
from dtr_operation import full_birthday, birthday_validator

BOT_TOKEN = environ.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

engine = create_engine(engine_settings)
session = sessionmaker(bind=engine)
s = session()

timeout_dict = {}

#ДНИ РОЖДЕНИЯ
#Реагируем на команду с днями рождения
@dp.message_handler(commands=['mybirthday'])
async def mybirthday_message(message):
    '''
    Выводит или изменяет день рождения пользователя
    '''
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    user_message = message.text[12:]

    #Отрезаем имя бота, если команда выбрана из списка
    if user_message == 'ZoroasterOfTomskBot': user_message = ''

    #Получаем день рождения пользователя из базы
    user_birthday = s.query(Birthday, User).join(User).filter(Birthday.chat_id == chat_id).filter(Birthday.telegram_id == user_id).one_or_none()

    if user_message != '':
        validation_birthday = birthday_validator(user_message)
        if validation_birthday['status'] != False:
            if user_birthday != None:
                user_update = s.query(User).where(User.id_telegram == user_birthday.User.id_telegram).update({User.username:user_name,
                                    User.first_name: first_name,
                                    User.last_name: last_name,
                                    User.updated_at: datetime.now()})
                                    
                birthday_update = s.query(Birthday).where(Birthday.telegram_id == user_birthday.Birthday.telegram_id).update({Birthday.birthday: validation_birthday['date'],
                                    Birthday.updated_at: datetime.now()})
                s.commit()
            else:
                s.add_all([User(id_telegram = user_id, username = user_name,
                            first_name = first_name,last_name = last_name,
                            created_at = datetime.now(), updated_at = datetime.now()),
                            Birthday(telegram_id = user_id, birthday = validation_birthday['date'],
                            chat_id = chat_id, created_at = datetime.now(),
                            updated_at = datetime.now())])
                s.commit()
            await message.reply('День рождения записан!')
        else:
            await message.reply('Неправильный формат дня рождения.')
    elif user_birthday != None and user_message == '':
        birthday_for_message = full_birthday(user_birthday.Birthday.birthday)
        await message.reply(f'У тебя зарегистрирован день рождения {birthday_for_message}.')
    else:
        await message.reply('У тебя не зарегистрирован день рождения. Набери "/mybirthday <ДДММ>". '
        'Например, для 11 сентября будет /mybirthday 1109.')

#Выводим список дней рождения
@dp.message_handler(commands=['allbirthday'])
async def allbirthday_message(message):
    '''
    Выводит список всех дней рождения
    '''
    chat_id = message.chat.id
    chat_birthdays = s.query(Birthday, User).join(User).filter(Birthday.chat_id == chat_id).order_by(Birthday.birthday).all()

    if chat_birthdays != []:
        birthday_list = ['Дни рождения всех уважаемых членов группы:']
        for row in chat_birthdays:
            username = row.User.username
            birthday = full_birthday(row.Birthday.birthday)
            if username == None:
                username = (row.User.first_name or '') + ' ' + (row.User.last_name or '')
            birthday_list.append(f'{username} - {birthday }')
        birthday_message = '\n'.join(birthday_list)
        await bot.send_message(chat_id, birthday_message)
    else:
        await message.reply('В чате не зарегистрированы дни рождения.')


#ШИТПОСТИНГ
@dp.message_handler(content_types=['text'])
async def get_text_messages(message):
    '''
    Читает сообщения в чате и отвечает на них.
    '''
    #Запускаем алгоритм, только если прошло 2 минуты с последнего сообщения, на который поступил ответ
    if timeout_dict.get(message.chat.id) == None or (int(time()) - timeout_dict[message.chat.id]['last_message'] > timeout_dict[message.chat.id]['timeout']):
        dice = lambda: randint(0, 100) #получаем рандомное число для просчета вероятности
        last_time_mark = int #создаем переменную для хранения последней временной метки сохранения базы с фразами

        #Загружаем словарь слов из БД
        words_dict = s.query(Word).all()

        for row in words_dict:
            word = row.word
            probability = row.probability

            get_text = message.text.lower() #получаем текст сообщения и делаем все буквы строчными
            get_text = get_text.replace('ё', 'е')

            #Получаем позицию из БД, сохраняем её для формирования среза, задаем максимальную длину сообщения
            position_dict = {
                            'no matter': [0, None, len(get_text)],
                            'begin': [None, len(word), len(word) + 3],
                            'end' : [-len(word), None, len(get_text)]
                            }
            position = position_dict[row.position]

            if word in get_text[position[0]:position[1]] and dice() < probability and len(get_text) <= position[2]:
                answer_dict = s.query(Answer).filter(Answer.word_id == row.id_word).all()
                answer_list = [row.answer for row in answer_dict]
                random_answer_index = randint(1, len(answer_list)) - 1
                answer = answer_list[random_answer_index]
                
                timeout_dict[message.chat.id] = {'last_message':int(time())}
                timeout_dict[message.chat.id]['timeout'] = randint(600, 3600)

                await message.reply(answer)
                break

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)