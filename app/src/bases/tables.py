from os import environ
from sqlalchemy import Column, ForeignKey, BigInteger, Integer, String, Boolean, Text, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import relationship  
from sqlalchemy import create_engine 

POSTGRES_DB = environ.get("POSTGRES_DB")
POSTGRES_USER = environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD")

engine_settings = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres_db:5432/{POSTGRES_DB}"
engine = create_engine(engine_settings)
Base = declarative_base()

class Group(Base):
    '''
    Класс для работы с базой групп
    '''
    __tablename__ = 'groups'

    id_telegram = Column(BigInteger, primary_key=True, autoincrement = False)
    chat_name = Column(String, nullable=False)
    posting_selector = Column(Boolean)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

class Word(Base):
    '''
    Класс для работы с базой слов
    '''
    __tablename__ = 'words'  
    
    id_word = Column(Integer, primary_key=True)  
    word = Column(Text, nullable=False, unique = True)  
    probability = Column(Integer, nullable=False)
    position = Column(String(10), nullable=False)
    selector = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    answers = relationship("Answer", back_populates="words")

class Answer(Base):
    '''
    Класс для работы с базой ответов к словам
    '''
    __tablename__ = 'answers'  
    
    id_answer = Column(Integer, primary_key=True)
    word_id = Column(ForeignKey("words.id_word")) 
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False) 
    words = relationship("Word", back_populates="answers")

class User(Base):
    '''
    Класс для работы с базой пользователей
    '''
    __tablename__ = 'users'
    
    id_telegram = Column(BigInteger, primary_key=True, autoincrement = False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    birthdays = relationship("Birthday", back_populates="users")

class Birthday(Base):
    '''
    Класс для работы с базой дней рождения
    '''
    __tablename__ = 'birthdays'

    id_birthday = Column(Integer, primary_key=True)
    telegram_id = Column(ForeignKey('users.id_telegram'))
    birthday = Column(Date, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    users = relationship("User", back_populates="birthdays")

Base.metadata.create_all(engine)