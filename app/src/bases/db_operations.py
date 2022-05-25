from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .tables import engine_settings, Base, Group, Word, Answer, User, Birthday
from .dtr_operation import full_birthday, birthday_validator

engine = create_engine(engine_settings)
session = sessionmaker(bind=engine)
s = session()

class DBOperation:
    '''
    Класс для работы с базой данных
    '''
    def __init__(self, message):
        self.chat_id = message.chat.id
        self.chat_name = message.chat.full_name
        self.user_id = message.from_user.id
        self.user_name = message.from_user.username
        self.first_name = message.from_user.first_name
        self.last_name = message.from_user.last_name
        self.message_text = message.text

class GroupOperation(DBOperation):
    '''
    Класс для работы с группами
    '''
    def add_group(self):
        '''
        Добавляет информацию о группе в базу
        '''
        s.add_all([Group(id_telegram = self.chat_id, chat_name = self.chat_name,
                    created_at = datetime.now(), updated_at = datetime.now())])

        s.commit()

    def update_group(self):
        '''
        Обновляет информацию о группе в базе
        '''
        s.query(Group).where(Group.id_telegram == self.chat_id).\
                        update({Group.chat_name:self.chat_name, Group.updated_at: datetime.now()})

        s.commit()

    def change_posting_selector(self, selector):
        '''
        Включает или выключается шитпостинг в чате
        '''
        s.query(Group).where(Group.id_telegram == self.chat_id).\
                        update({Group.posting_selector:selector, Group.updated_at: datetime.now()})
        
        s.commit()

class BirthdayOperation(DBOperation):
    '''
    Класс для работы с днями рождения
    '''       
    def get_user_birthday(self, user_message):
        '''
        Загружает день рождения пользователя из БД
        '''
        self.user_birthday = s.query(Birthday, User).join(User).filter(Birthday.chat_id == self.chat_id).\
                        filter(Birthday.telegram_id == self.user_id).one_or_none()
        
        self.validation_birthday = birthday_validator(user_message)

        self.user_message = user_message

        if self.user_birthday != None:
            self.full_birthday = full_birthday(self.user_birthday.Birthday.birthday)
        else:
            self.full_birthday = None

    def update_user_birthday(self):
        '''
        Обновляет день рождения пользователя в БД
        '''
        user_update = s.query(User).where(User.id_telegram == self.user_birthday.User.id_telegram).update({User.username:self.user_name,
                                User.first_name: self.first_name,
                                User.last_name: self.last_name,
                                User.updated_at: datetime.now()})
                                
        birthday_update = s.query(Birthday).where(Birthday.telegram_id == self.user_birthday.Birthday.telegram_id).\
                                update({Birthday.birthday: birthday_validator(self.user_message)['date'],
                                Birthday.updated_at: datetime.now()})
        s.commit()

    def add_user_birthday(self):
        '''
        Добавляет день рождения пользователя в БД
        '''
        s.add_all([User(id_telegram = self.user_id, username = self.user_name,
                    first_name = self.first_name,last_name = self.last_name,
                    created_at = datetime.now(), updated_at = datetime.now()),
                    Birthday(telegram_id = self.user_id, birthday = birthday_validator(self.user_message)['date'],
                    chat_id = self.chat_id, created_at = datetime.now(),
                    updated_at = datetime.now())])

        s.commit()

    def get_all_birthday(self):
        '''
        Возвращает список всех дней рождения в группе из БД
        '''
        chat_birthdays = s.query(Birthday, User).join(User).filter(Birthday.chat_id == self.chat_id).order_by(Birthday.birthday).all()
        if chat_birthdays == []:
            result = []
        else:
            birthday_list = []
            for row in chat_birthdays:
                username = row.User.username
                birthday = full_birthday(row.Birthday.birthday)
                if username == None:
                    username = (row.User.first_name or '') + ' ' + (row.User.last_name or '')
                birthday_list.append(f'{username} - {birthday }')
                result = birthday_list
        
        return result

class PostingOperation(DBOperation):
    '''
    Класс для работы с ответами на слова
    '''
    def get_word_dict(self):
        '''
        Возвращает словарь слов из БД
        '''
        result = s.query(Word).all()

        return result

    def get_answer_list(self, id_word):
        '''
        Возвращает ответов на слово из БД
        '''
        answer_dict = s.query(Answer).filter(Answer.word_id == id_word).all()
        result = [row.answer for row in answer_dict]

        return result