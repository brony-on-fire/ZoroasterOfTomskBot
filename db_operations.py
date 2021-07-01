'''
Модуль предназначен для редактирования фраз,
для бота, хранящихся в базе данных redis
'''
#/usr/bin/env python3

import redis
from random import getrandbits
from typing import List

r = redis.Redis(decode_responses = True)

#Наименование словарей
words_hash = 'words' 

def get_word_list() -> List[str]:
    '''
    Функция для возврата списка всех доступных слов,
    на которые реагирует бот.
    '''
    list_hash = r.hkeys(words_hash)

    return list_hash

def view_word_info(list_hash: List[str], word_for_edit: int):
    '''
    Функция для просмотра информации о выбранном слове.
    '''
    if word_for_edit >= 0 and word_for_edit < len(list_hash):
        id_answer_of_word = r.hget(words_hash, list_hash[word_for_edit])
        info_of_word = r.hgetall(id_answer_of_word)
    else:
        info_of_word = f'Слово с индексом "{word_for_edit}" не найдено!'

    return info_of_word

def add_new_word(word: str, answer: str, probability: int, position: str) -> str:
    '''
    Функция для добавление нового слова,
    на которое будет реагировать бот.
    '''
    id_answer_of_word = f'word:{getrandbits(32)}:hash'
    params = {
        'answer':answer, 'probability':probability,
        'position': position, 'selector': '1'
        }
    r.hmset(id_answer_of_word, params)
    r.hmset(words_hash, {word:id_answer_of_word})

    return 'OK'

def show_last_save() -> int:
    timme_mark = r.lastsave()

    return timme_mark


if __name__ == '__main__':
    print('Добро пожаловать, Господин!\nДля выхода из программы напиши "exit"')

    next_step = str
    while next_step != 'exit':
        print('Для выбора действия нажми:',
            '1. Просмотреть список слов, на которые реагирует бот - "1"',
            '2. Добавить новое слово - "2".',
            sep = "\n")
        next_step = input()
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


    
