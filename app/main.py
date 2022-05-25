from aiogram import executor
from create_bot import dp
from src.handlers import birthdays, posting

#Дни рождения
birthdays.register_handlers_birthdays(dp)

#Шитпостинг
posting.register_handlers_posting(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)