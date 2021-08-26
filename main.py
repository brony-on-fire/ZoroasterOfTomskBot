#/usr/bin/env python3

import sys, telebot, db_operations
from random import randint
from typing import List
from time import time

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

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    '''
    Читает сообщения в чате и отвечает на них.
    '''
    #Запускаем алгоритм, только если прошло 2 минуты с последнего сообщения, на который поступил ответ
    if timeout_dict.get(message.chat.id) == None or (int(time()) - timeout_dict[message.chat.id] > 120):
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
                timeout_dict[message.chat.id] = int(time())
                break

bot.polling(none_stop=True, interval=0)