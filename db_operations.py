'''
Модуль предназначен для редактирования фраз
для бота, хранящихся в базе данных redis
'''
#/usr/bin/env python3

import redis, time
from random import getrandbits
from typing import Dict, List
from base64 import b64encode, b64decode

r = redis.Redis(decode_responses = True)

#СЛОВАРЬ ДЛЯ ШИТПОСТИНГА
#Наименование словарей
words_hash = 'words' 

def get_word_list() -> List[str]:
    '''
    Возвращает список всех доступных слов, на которые реагирует бот.
    '''
    list_hash = r.hkeys(words_hash)

    return list_hash

def view_word_info(list_hash: List[str], word_for_edit: int):
    '''
    Отображает информации о выбранном слове.
    '''
    if word_for_edit >= 0 and word_for_edit < len(list_hash):
        id_answer_of_word = r.hget(words_hash, list_hash[word_for_edit])
        info_of_word = r.hgetall(id_answer_of_word)
    else:
        info_of_word = f'Слово с индексом "{word_for_edit}" не найдено!'

    return info_of_word

def add_new_word(word: str, answer: str, probability: int, position: str) -> str:
    '''
    Добавляет новое слово, на которое будет реагировать бот.
    '''
    id_answer_of_word = f'word:{getrandbits(32)}:hash'
    params = {
        'answer':answer, 'probability':probability,
        'position': position, 'selector': '1'
        }
    r.hmset(id_answer_of_word, params)
    r.hmset(words_hash, {word:id_answer_of_word})

    return 'OK'

def parametr_of_word_edit(word_for_edit: int, params: Dict, list_hash: List[str]):
    '''
    Редактирует параметры выбранного слова.
    '''
    id_answer_of_word = r.hget(words_hash, list_hash[word_for_edit])
    r.hmset(id_answer_of_word, params)
        
def show_last_save() -> int:
    '''
    Возвращает дату и время последнего изменения в БД.
    '''
    timme_mark = r.lastsave()

    return timme_mark

#СЛОВАРЬ ДЛЯ ДНЕЙ РОЖДЕНИЙ

def get_birthday(chat_id: int):
    '''
    Извлекает дни рождения из словаря
    '''
    birthdays_id = f"birthday:{chat_id}"
    birthdays_hash = r.hgetall(birthdays_id)
    
    return birthdays_hash

def decode_birthdays(birthdays_hash):
    '''
    Декодирует значения словаря из base64 в список
    '''
    for key in birthdays_hash:
        birthdays_hash[key] = b64decode(birthdays_hash[key])
        birthdays_hash[key] = birthdays_hash[key].decode("utf-8")
        birthdays_hash[key] = birthdays_hash[key].split(':')

    return birthdays_hash

def encode_birthday(user_id: str, user_name: str, birthday: str):
    '''
    Кодируем значение словаря из списка в base64
    '''
    birthday = f"{user_id}:{user_name}:{birthday}".encode('utf-8')
    birthday = b64encode(birthday)

    return birthday

def put_birthday(user_id: str, user_name: str, chat_id: int, birthday:str):
    '''
    Добавляет день рождения в словарь
    '''
    #Проверяем, что дата в правильном формате
    if len(birthday) != 4:
        return "Неправильный формат дня рождения."

    try:
        time.strptime(birthday, "%d%m")
    except ValueError:
        return "Неправильный формат дня рождения."

    #Достём словарь с днями рождения и изменяем дату
    chat_birthdays = get_birthday(chat_id)

    #Преобразовываем данные о пользователе и его дате рождения
    birthday = encode_birthday(user_id, user_name, birthday)

    #Записываем обработанные данные в redis
    chat_birthdays[user_id] = birthday

    #Сохраняем словарь с датами рождения
    r.hmset(f"birthday:{chat_id}", chat_birthdays)
    return "День рождения записан!"

#Меню для просмотра и редактирования слов
if __name__ == '__main__':
    print('Добро пожаловать, Господин!\nДля выхода из программы напиши "exit"')

    next_step = str
    while next_step != 'exit':
        print('Для выбора действия нажми:',
            '1. Просмотреть список слов, на которые реагирует бот - "1"',
            '2. Добавить новое слово - "2".',
            sep = "\n"
            )
        next_step = input()
        
        #Раздел просмотра слов
        if next_step == "1":
            list_hash = get_word_list()

            for i in range(0, len(list_hash)):
                print(f'{i+1}. {list_hash[i]}')

            while True:
                word_for_edit = input('Наберите номер слова, с которым необходимо поработать, либо ENTER для выхода.')
                if word_for_edit == '': break
                word_for_edit = int(word_for_edit)-1
                word_info = view_word_info(list_hash, word_for_edit)
                
                if type(word_info) != dict:
                    print(word_info)
                elif type(word_info) == dict: 
                    answer = word_info['answer']
                    probability = word_info['probability']
                    position = word_info['position']
                    selector = word_info['selector']
                    print(
                        f'Слово: "{list_hash[word_for_edit]}"\n'+
                        f'Ответ: "{answer}"\nВероятность: {probability}\n' + 
                        f'Позиция: {position}\nСостояние: {selector}\n'
                        )
                
                #Подраздел для редактирования слова
                while True:
                    print(
                    'Ответ - 1',
                    'Вероятность - 2', 
                    'Позиция - 3', 
                    'Состояние - 4',
                    sep = '\n'
                    )
                    position_for_edit = input('Наберите номер параметра, который необходимо отредактировать, либо ENTER для выхода.')
                    if position_for_edit == '': break
                    position_for_edit = int(position_for_edit)

                    if position_for_edit not in range(1, 5):
                        print('Нет такого параметра!')
                    else:
                        new_parametr = input('Введите новое значение параметра: ')
                        param_list = ['answer', 'probability', 'position', 'selector']
                        new_parametr = {param_list[position_for_edit-1]:new_parametr}
                        parametr_of_word_edit(word_for_edit, new_parametr, list_hash)

        #Раздел добавления слова
        elif next_step == "2":
            word = input("Введите слово: ")
            answer = input("Введите ответ на слово: ")
            probability = int(input("Введите вероятность ответа на слово: "))
            
            position = str
            while type(position) != str :
                position = int(input("Выбирите позицию в тексте (1 - не важно, 2 - начало, 3 - конец): "))
                if position == 1:
                    position = 'no matter'
                elif position == 2:
                    position = 'begin'
                elif position == 3:
                    position = 'end'
            
            add_new_word(word, answer, probability, position)