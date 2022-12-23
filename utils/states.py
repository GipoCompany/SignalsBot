from aiogram.dispatcher.filters.state import StatesGroup, State

class SetBalance(StatesGroup):
    balance = State()
    message = State()

class Wallet(StatesGroup):
    call = State()
    wallet = State()

class Settings(StatesGroup):
    start_msg = State()
    using_msg = State()
    getsign_msg = State()
    suborsign_msg = State()
    setpaymethod_msg = State()
    buysub_msg = State()
    buysub_price = State()
    first_buysub_price = State()
    buysign_msg = State()
    buysign_price = State()
    wallet = State()

class Uid(StatesGroup):
    user_id = State()

class Stats(StatesGroup):
    button = State()
    date = State()