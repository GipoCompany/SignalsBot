from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def paymethods(user_id: int, paymethods: list, balance: float):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for method in paymethods:
        name, status = method.split(":")
        status = int(status)
        buttons.append(InlineKeyboardButton(f"{name} {'✅' if status else ''}", callback_data=f"paymethod_{name}:{user_id}:{status}"))
    markup.add(*buttons)
    markup.add(InlineKeyboardButton(f"Баланс: {balance}₽", callback_data=f"paymethod_balance:{user_id}:0"))
    markup.add(InlineKeyboardButton("Получить сигнал", callback_data=f"paymethod_continue:{user_id}:0"))
    return markup

async def signal(user_id, subscribe, arg=None):
    markup = InlineKeyboardMarkup(row_width=1)
    if arg:
        buttons = [InlineKeyboardButton(text, callback_data=f"signal_{callback}:{user_id}") for text, callback in {"меню": "menu"}.items()]
        markup.add(*buttons)
        return markup
    if not subscribe:
        markup.add(InlineKeyboardButton("Не успел воспользоваться", callback_data=f"signal_dontuse:{user_id}"))
    buttons = [InlineKeyboardButton(text, callback_data=f"signal_{callback}:{user_id}") for text, callback in {"Новый сигнал": "newsignal", "меню": "menu"}.items()]
    markup.add(*buttons)
    return markup

async def setbalance(user_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("назад", callback_data=f"setbalance_back_{user_id}"))
    return markup