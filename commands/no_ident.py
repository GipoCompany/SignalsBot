import logging
from aiogram import Dispatcher, types

async def no_ident_but(call: types.CallbackQuery):
    logging.warning(f"НЕ ОПОЗНАНАЯ КНОПКА: {call.data}")

async def no_ident_commands(msg: types.Message):
    logging.warning(f"НЕ ОПОЗНАНАЯ КОМАНДА: {msg.text}")

async def load(dp: Dispatcher):
    dp.register_callback_query_handler(no_ident_but)
    dp.register_message_handler(no_ident_commands, lambda msg: msg.text.startswith("/"))