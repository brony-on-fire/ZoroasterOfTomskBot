from aiogram import Bot, Dispatcher
from os import environ

BOT_TOKEN = environ.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)