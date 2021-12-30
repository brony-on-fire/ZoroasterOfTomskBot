#/usr/bin/env python3

import sys, telebot, db_operations
from random import randint
from typing import List
from time import time
from dtr_operation import full_birthday, sorted_birthday

arguments = sys.argv[:]
token = arguments[1]

def get_word_dict() -> List[str]:
    '''
    Загружает словари из БД
    '''
    word_list = db_operations.get_word_list()
    word_dict = {}
    for i in range(0, len(word_list)):
        upload_answer = db_operations.view_word_info(word_list, i)
        word_dict[word_list[i]] = upload_answer

    return word_dict

bot = telebot.TeleBot(token)
timeout_dict = {}

#ДНИ РОЖДЕНИЯ
#Реагируем на команду с днями рождения
@bot.message_handler(commands=['mybirthday'])
def mybirthday_message(message):
    '''
    Выводит или изменяет день рождения пользователя
    '''
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    user_name = message.from_user.username
    if user_name is None: user_name = (message.from_user.first_name + ' ' + message.from_user.last_name)
    user_message = message.text[12:]

    #Отрезаем имя бота, если команда выбрана из списка
    if user_message == 'ZoroasterOfTomskBot': user_message = ''

    chat_birthdays = db_operations.decode_birthdays(db_operations.get_birthday(chat_id))
    if user_message != '':
        action_for_birthday = db_operations.put_birthday(user_id, user_name, chat_id, user_message)
        bot.send_message(chat_id, action_for_birthday, reply_to_message_id = message.message_id)
    elif chat_birthdays.get(user_id) != None and user_message == '':
        birthday_for_message = full_birthday(chat_birthdays[user_id][2])
        bot.send_message(chat_id, f'У тебя зарегистрирован день рождения {birthday_for_message}.', reply_to_message_id = message.message_id)
    else:
        bot.send_message(chat_id, 'У тебя не зарегистрирован день рождения. Набери "/mybirthday <ДДММ>". '
        'Например, для 11 сентября будет /mybirthday 1109.', reply_to_message_id = message.message_id)

#Выводим список дней рождения
@bot.message_handler(commands=['allbirthday'])
def allbirthday_message(message):
    chat_id = message.chat.id
    chat_birthdays = db_operations.decode_birthdays(db_operations.get_birthday(chat_id))
    if len(chat_birthdays) != 0:
        #Сортируем дни рождения и добавляем к сообщению
        birthday_list = ['Дни рождения всех уважаемых членов группы:'] + sorted_birthday(chat_birthdays)
        birthday_message = '\n'.join(birthday_list)
        bot.send_message(chat_id, birthday_message)
    else:
        bot.send_message(chat_id, 'В чате не зарегистрированы дни рождения.', reply_to_message_id = message.message_id)

#ШИТПОСТИНГ
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    '''
    Читает сообщения в чате и отвечает на них.
    '''
    #Запускаем алгоритм, только если прошло 2 минуты с последнего сообщения, на который поступил ответ
    if timeout_dict.get(message.chat.id) == None or (int(time()) - timeout_dict[message.chat.id]['last_message'] > timeout_dict[message.chat.id]['timeout']):
        dice = lambda: randint(0, 100) #получаем рандомное число для просчета вероятности
        last_time_mark = int #создаем переменную для хранения последней временной метки сохранения базы с фразами

        #Загружаем словарь из redis только если были изменения БД
        time_mark = db_operations.show_last_save()
        if time_mark != last_time_mark:
            word_dict = get_word_dict()
            time_mark = last_time_mark

        for word in word_dict:
            answer = word_dict[word]['answer']
            probability = int(word_dict[word]['probability'])

            get_text = message.text.lower() #получаем текст сообщения и делаем все буквы строчными
            get_text = get_text.replace('ё', 'е')

            #Получаем позицию из redis, сохраняем её для формирования среза, задаем максимальную длину сообщения
            position_dict = {
                            'no matter': [0, None, len(get_text)],
                            'begin': [None, len(word), len(word) + 3],
                            'end' : [-len(word), None, len(get_text)]
                            }
            position = position_dict[word_dict[word]['position']]

            if word in get_text[position[0]:position[1]] and dice() < probability and len(get_text) <= position[2]:
                bot.send_message(message.chat.id, answer, reply_to_message_id = message.message_id)
                timeout_dict[message.chat.id] = {'last_message':int(time())}
                timeout_dict[message.chat.id]['timeout'] = randint(600, 3600)
                break

bot.polling(none_stop=True, interval=0)