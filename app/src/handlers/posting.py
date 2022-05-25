from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter
from random import randint
from time import time
from src.bases.db_operations import PostingOperation
from create_bot import dp

timeout_dict = {}

async def posting(message:types.Message):
    '''
    Читает сообщения в чате и отвечает на них.
    '''
    #Запускаем алгоритм, только если прошло 2 минуты с последнего сообщения, на который поступил ответ
    if timeout_dict.get(message.chat.id) == None or (int(time()) - timeout_dict[message.chat.id]['last_message'] > timeout_dict[message.chat.id]['timeout']):
        dice = lambda: randint(0, 100) #получаем рандомное число для просчета вероятности
        last_time_mark = int #создаем переменную для хранения последней временной метки сохранения базы с фразами

        #Загружаем словарь слов из БД
        words_dict = PostingOperation(message).get_word_dict()

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
                answer_list = PostingOperation(message).get_answer_list(row.id_word)
                random_answer_index = randint(1, len(answer_list)) - 1
                answer = answer_list[random_answer_index]
                
                timeout_dict[message.chat.id] = {'last_message':int(time())}
                timeout_dict[message.chat.id]['timeout'] = randint(600, 3600)

                await message.reply(answer)
                break

def register_handlers_posting(dp:Dispatcher):
    dp.register_message_handler(posting, ChatTypeFilter(chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP]), content_types=['text'])