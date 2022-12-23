import logging
from datetime import datetime, timedelta
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import BotCommand, BotCommandScopeChat
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text

from utils.config import Tokens
from utils.signals.algorithm.logic import OrderSet
from utils.time_generator import time_generator
from utils import database as db
from utils.signals.algorithm import get_orders
from utils.signals.algorithm.logic import OrderSet
import buttons
import commands

__version__ = "1.5b"

SIGNALS = OrderSet(None, None, None)

logging.basicConfig(level=logging.INFO, format="%(asctime)s || %(levelname)s || %(message)s")

bot = Bot(Tokens.test, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage(), loop=asyncio.get_event_loop())

async def on_startup(dp: Dispatcher):
    await commands.load(dp)
    await dp.bot.set_my_commands([BotCommand("start", "меню")])
    for user in await db.get.users(access_lvl=2):
        await dp.bot.set_my_commands([BotCommand("start", "меню"), BotCommand("admins", "список админ команд")], scope=BotCommandScopeChat(user.user_id))

    dp.info = await bot.get_me()
    dp.startup_time = datetime.now()

    list_bot_msg = await dp.bot.forward_message(chat_id=1104748610, from_chat_id=-1001574337755, message_id=19)
    await list_bot_msg.delete()
    list_bot_msg = list_bot_msg.text.split("• ")
    c = 0
    for i in list_bot_msg:
        list_bot_msg[c] = list_bot_msg[c].strip()
        if i.startswith(dp.info.mention):
            list_bot_msg[c] = f"{dp.info.mention}\n  статус: 🟢\n  включен: {dp.startup_time.strftime('%H:%M %d.%m.%Y')}"
        c += 1
    await dp.bot.edit_message_text("\n• ".join(list_bot_msg), chat_id=-1001574337755, message_id=19)

async def on_shutdown(dp):
    list_bot_msg = await dp.bot.forward_message(chat_id=1104748610, from_chat_id=-1001574337755, message_id=19)
    await list_bot_msg.delete()
    list_bot_msg = list_bot_msg.text.split("• ")
    c = 0
    for i in list_bot_msg:
        list_bot_msg[c] = list_bot_msg[c].strip()
        if i.startswith(dp.info.mention):
            list_bot_msg[c] = f"{dp.info.mention}\n  статус: ⭕\n  выключен: {datetime.now().strftime('%H:%M %d.%m.%Y')}\n  время работы:{time_generator(datetime.now(), dp.startup_time)}"
        c += 1
    await dp.bot.edit_message_text("\n• ".join(list_bot_msg), chat_id=-1001574337755, message_id=19)

async def checksub():
    while True:
        if datetime.now().strftime("%d") == "1":
            await db.edit.users(reserve_signal=3)
        users = await db.get.users()
        count = 0
        for user in users:
            if -1 < (days := (user.subscribe - datetime.now()).days) < 6:
                if count == 5:
                    await asyncio.sleep(60)
                    count = 0
                count += 1
                await bot.send_message(user.user_id, f"Ваша подписка закончится через {days} {'день' if days == 1 else ('дней' if days in [5, 0] else 'дня')}!", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Продлить", callback_data=f"extand_sub_{user.user_id}")))
        logging.info("Subs checked")
        await asyncio.sleep(24*60*60)

@dp.callback_query_handler(Text(startswith="extand_sub_"))
async def extand_sub_(call: types.CallbackQuery):
    user_id = call.data.replace("extand_sub_", "")
    user, settings = await db.get.users(user_id=user_id), await db.get.settings()
    price = settings.buysub_price if user.subscribe_count > 25 else settings.first_buysub_price
    await call.message.answer(settings.buysub_msg.format(price=price, walletTRC20=settings.walletTRC20, walletBEP20=settings.walletBEP20), reply_markup=await buttons.start.buy(user_id, price, "sub"))

@dp.message_handler(commands=["sub"])
async def get_sub(msg: types.Message):
    user = await db.check(msg)
    if user.subscribe > datetime.now():
        await db.edit.users(user.user_id, subscribe=f"'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'", access_lvl=1)
        await msg.reply("У вас отозвана подписка и уровень доступа админа")
        await dp.bot.set_my_commands([BotCommand("start", "меню")], scope=BotCommandScopeChat(user.user_id))
    else:
        await db.edit.users(user.user_id, subscribe=f"'{(datetime.now() + timedelta(days=30.5)).strftime('%Y-%m-%d %H:%M:%S')}'", access_lvl=2)
        await msg.reply("Вам выдана подписка и уровень доступа админа")
        await dp.bot.set_my_commands([BotCommand("start", "меню"), BotCommand("admins", "список админ команд")], scope=BotCommandScopeChat(user.user_id))


#async def getsignals():
#    global SIGNALS
#
#    while True:
#        SIGNALS = await get_orders()
#        logging.info("Signals updated")
#        await asyncio.sleep(60)

if __name__ == '__main__':
    dp.loop.create_task(checksub())
#    dp.loop.create_task(getsignals())
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)