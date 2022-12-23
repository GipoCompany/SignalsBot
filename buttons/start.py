from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def main(user_id: int):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(*[InlineKeyboardButton(k, callback_data=f"{v}:{user_id}") for k,v in {'Как пользоваться ботом?': 'start_using', 'Получить сигнал': 'start_getsign'}.items()])
    return markup

async def using(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("меню", callback_data=f"using_back:{user_id}"))
    return markup

async def setpaymethod(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Заполнить данные", callback_data=f"setpaymethod:{user_id}"))
    return markup

async def suborsign(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Купить подписку", callback_data=f"suborsign_buysub:{user_id}"))
    markup.add(InlineKeyboardButton("Купить сигнал", callback_data=f"suborsign_buysign:{user_id}"))
    markup.add(InlineKeyboardButton("Меню", callback_data=f"suborsign_menu:{user_id}"))
    return markup

async def buy(user_id, price, type):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Проверить оплату", callback_data=f"buy_{type}:{user_id}:{price}"))
    return markup
