from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- Выбор чата для администрирования ---
class ChatButton:
    '''
    Класс для формирования меню со списком администрируемых групп
    '''
    def __init__(self, chats):
        self.chats = chats
        for key in self.chats:
            self.chats[key]['button'] = KeyboardButton(chats[key]['name'])
        
        self.chats_list = [f"⚙️ {key['button']}&&{key['id']}" for key in self.chats]
    
    def menu(self):
        self.chatsMenu = ReplyKeyboardMarkup(resize_keyboard = True).add(*chats_list)

        return self.chatsMenu

# --- Меню параметров для администрирования ---
btnWords = KeyboardButton('⚙️ Слова')
btnAnswers = KeyboardButton('⚙️ Ответы')
optionsMenu = ReplyKeyboardMarkup(resize_keyboard = True).add(btnWords, btnAnswers)