from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def give_signal_(user_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(*[InlineKeyboardButton(text, callback_data=f"give_signal_{but}:{user_id}") for text, but in {'Всем': 'all', 'Пользователю': 'user'}.items()])
    return markup

async def stats_(user_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(*[InlineKeyboardButton(text, callback_data=f"stats_{butt}:{user_id}") for text, butt in {'Средний спред за': "10", "Самый высокий спред за": "11", "Количество связок за": "12"}.items()])
    return markup