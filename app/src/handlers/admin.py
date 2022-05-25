from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter
import markups as nav
from create_bot import dp

async def main_menu(message:types.Message):
    await message.answer('Что хотите администрировать?', reply_markup = nav.optionsMenu)

async def submenu(message:types.Message):
    await message.answer(message.text)

def register_handlers_admin(dp:Dispatcher):
    dp.register_message_handler(main_menu, ChatTypeFilter(chat_type=types.ChatType.PRIVATE), commands = ['admin'])
    dp.register_message_handler(submenu, ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith = ['⚙️'])