import asyncio
from datetime import datetime, timedelta
import datetime as mdatetime

import aiogram
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from buttons.get_signal import signal

from main import bot
import buttons
from buttons import admins as kb
from utils import database as db
import utils.types as mytypes
from utils import states

async def admins_(msg: types.Message):
    user = await db.check(msg)
    if user.access_lvl > 1:
        await msg.reply("""
Эти команды доступны только администраторам!

/give_signal - Выдает бесплатный сигнал пользователю(ям)
/stats - статистика
/all_signals (сумма) - возвращает .txt файл со всеми найдеными сигналами и ордерами(по указанной сумме)
/all_orders - возвращает .txt файл со всеми ордерами найденными в данный момент времени
""")

async def give_signal_(msg: types.Message):
    user = await db.check(msg)
    if user.access_lvl < 2:
        return
    await msg.reply("Выберети вариант:", reply_markup=await kb.give_signal_(msg.from_user.id))

async def rassilka(time, finish=False, **kwargs):
    c = 0
    c2 = 0
    users = await db.get.users(**kwargs)
    users = users if isinstance(users, list) else [users]
    for user in [i for i in users if i.subscribe < datetime.now() and i.signal_free > 0]:
        if c > 5:
            await asyncio.sleep(60)
            c = 0
        try:
            if finish == "first":
                await bot.send_message(user.user_id, f"🎁 Поздравляем! \n\nТы получил подарочный сигнал, которым можешь воспользоваться в течение {time} 💸\n\n⚜️ Не упусти свою возможность получить дополнительную прибыль", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Воспользоваться сигналом", callback_data=f"start_getsign:{user.user_id}")))
            elif not finish:
                await bot.send_message(user.user_id, f"🚨 Успей воспользоваться подарочным сигналом!\n\n⏳ До момента завершения срока действия предложения осталось: <b>{time}</b>", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Воспользоваться сигналом", callback_data=f"start_getsign:{user.user_id}")))
            else:
                await bot.send_message(user.user_id, "Ваш подарочный сигнал сгорел(")
        except:
            continue
        c += 1
        c2 += 1
    return c2

async def sheduler_(**kwargs):
    await rassilka('24 часов', "first", **kwargs)
    await asyncio.sleep(6*60*60)
    await rassilka('18 часов', **kwargs)
    await asyncio.sleep(6*60*60)
    await rassilka('12 часов', **kwargs)
    await asyncio.sleep(6*60*60)
    await rassilka('6 часов', **kwargs)
    await asyncio.sleep(4*60*60)
    await rassilka('2 часа', **kwargs)
    await asyncio.sleep(1.5*60*60)
    await rassilka('30 минут', **kwargs)
    await asyncio.sleep(30*60)
    await rassilka('', True, **kwargs)

async def gsign_buttons_(call: types.CallbackQuery, state: FSMContext):
    but, user_id = call.data.replace("give_signal_", '').split(':')
    if but == 'all':
        count = await db.edit.users(arg="subscribe <= (now() + interval '3 hour')", signal_free="signal_free+1")
        await call.message.edit_text(f"Бесплатный сигнал выдан {len(count)} пользователям!")
        await sheduler_()
        count2 = await db.edit.users(arg="subscribe <= now() AND signal_free >= 1", signal_free="signal_free-1")
        await call.message.reply(f"{len(count2)}/{len(count)} не успели воспользоваться сигналом.")
    if but == 'user':
        await state.set_state(states.Uid.user_id.state)
        await call.message.edit_text(f"Введите id пользователя которому хотели бы дать сигнал")
        
async def give_user_id_(msg: types.Message, state: FSMContext):
    user = await db.get.users(user_id=msg.text.strip())
    if not user:
        await msg.reply(f"Пользователя с таким id не найдено. Введите другой айди или напишите /start для выхода из команды.")
        return await state.set_state(states.Uid.user_id.state)
    await state.finish()
    await db.edit.users(user_id=user.user_id, signal_free="signal_free+1")
    messag = await msg.reply(f"Бесплатный сигнал успешно выдан пользователю с id - {user.user_id}")
    await sheduler_(user_id=user.user_id)
    edit = await db.edit.users(arg=f"user_id={user.user_id} AND signal_free >= 1", signal_free="signal_free-1")
    await messag.reply(f"Пользователь с id - {user.user_id} {'успел' if not len(edit) else 'не успел'} воспользоваться бесплатным сигналом")

async def stats_(msg: types.Message):
    user = await db.check(msg)
    if user.access_lvl > 1:
        users = await db.get.users()
        signals = await db.get.signals()
        settings = await db.get.settings()
        try:
            signals_oborot = round(sum([user.signal_count*settings.buysign_price for user in users]) / (sum([sum([user.subscribe_count*settings.first_buysub_price, user.signal_count*settings.buysign_price] if user.subscribe_count <= 25 else [25*settings.first_buysub_price, (user.subscribe_count-25)*settings.buysub_price, user.signal_count*settings.buysign_price]) for user in users]) / 100), 1)
            sub_oborot = round(sum([sum([user.subscribe_count*settings.first_buysub_price] if user.subscribe_count <= 25 else [25*settings.first_buysub_price, (user.subscribe_count-25)*settings.buysub_price]) for user in users]) / (sum([sum([user.subscribe_count*settings.first_buysub_price, user.signal_count*settings.buysign_price] if user.subscribe_count <= 25 else [25*settings.first_buysub_price, (user.subscribe_count-25)*settings.buysub_price, user.signal_count*settings.buysign_price]) for user in users]) / 100), 1)
        except:
            signals_oborot = 0
            sub_oborot = 0
        text = """
🧮 СТАТИСТИКА

🧔🏽‍♂️ Зарегестрировано:
{one}

💬 Сейчас активно:
{two}

🗃️ Среднее количество купленных подписок на человека:
{free}

💎 Хотя бы 1 раз купили сигнал:
{four}

🔑 Среднее количество купленных сигналов на человека:
{five}

🔎 За всё время работы бота найдено:
{six}

💰 Самый высокий спред {seven}

🏆 Оборот за все время: {eight}
% оборота от:
    Сигналов - {nine}
    Подписок - {ten}
""".format(
    one=f'{len(users)} пользовател{"ей" if int(str(len(users))[-1]) in [0, 5, 6, 7, 8, 9] else ("я" if int(str(len(users))[-1]) in [2, 3, 4] else "ь")}.', 
    two=f'{len([i for i in users if i.subscribe > datetime.now()])} подпис{"ок" if int(str(len([i for i in users if i.subscribe > datetime.now()]))[-1]) in [0, 5, 6, 7, 8, 9] else ("ки" if int(str(len([i for i in users if i.subscribe > datetime.now()]))[-1]) in [2, 3, 4] else "ка")}.', 
    free=f'{round(sum([user.subscribe_count for user in users]) / len(users), 3)}',
    four=f'{len([i for i in users if i.signal_count])} пользовател{"ей" if int(str(len([i for i in users if i.signal_count]))[-1]) in [0, 5, 6, 7, 8, 9] else ("я" if int(str(len([i for i in users if i.signal_count]))[-1]) in [2, 3, 4] else "ь")}', 
    five=f'{round(sum([i.signal_count for i in users]) / len(users), 3)}', 
    six=f'{sorted(signals, key=lambda x: x.id, reverse=True)[0].id} связ{"ок" if int(str(sorted(signals, key=lambda x: x.id, reverse=True)[0].id)[-1]) in [0,5,6,7,8,9] else ("ки" if int(str(sorted(signals, key=lambda x: x.id, reverse=True)[0].id)[-1]) in [2, 3, 4] else "а")}',
    seven=f'{max(signals, key=lambda x: x.spread).spread}% был зафиксирован {max(signals, key=lambda x: x.spread).date.strftime("%d.%m.%Y в %H:%M")}', 
    eight=f"{sum([sum([user.subscribe_count*settings.first_buysub_price, user.signal_count*settings.buysign_price] if user.subscribe_count <= 25 else [25*settings.first_buysub_price, (user.subscribe_count-25)*settings.buysub_price, user.signal_count*settings.buysign_price]) for user in users])} USDT", 
    nine=f'{signals_oborot}%', 
    ten=f'{sub_oborot}%'
    )
        await msg.reply(text, reply_markup=await kb.stats_(user.user_id))

async def stats_but_(call: types.CallbackQuery, state: FSMContext):
    button, user_id = call.data.replace("stats_", "").split(":")
    await call.message.answer(f"Введите дату в одном из представленых ниже форматов для получения информации или напишите /start для сброса состояния.\n    yyyy (пример: 2022 (для получения информации за 2022 год))\n    mm.yyyy (пример: 09.2022 (для получения информации за сентябрь 2022 года))\n    dd.mm.yyyy (пример: 10.09.2022 (для получения информации за 10.09.2022))\n    dd.mm.yyyy - dd.mm.yyyy (пример 05.09.2022 - 10.09.2022 (для получения информации за отрезок с 5 по 10 число сентября))")
    await state.set_state(states.Stats.date)
    await state.update_data(button=int(button))

async def input_date(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if not msg.text.replace(" ", "").replace(".", "").replace("-", "").isdecimal():
        return await msg.reply("это не дата.")
    elif (lenmsg := len(msg.text)) == 4:
        date1 = datetime.strptime(msg.text, "%Y"), "year"
        date2 = date1[0] + timedelta(days=365.5)
    elif lenmsg == 7:
        date1 = datetime.strptime(msg.text, "%m.%Y"), "month"
        date2 = date1[0] + timedelta(days=30.5)
    elif lenmsg == 10:
        date1 = datetime.strptime(msg.text, "%d.%m.%Y"), "day"
        date2 = date1[0] + timedelta(hours=24)
    elif lenmsg == 23:
        date1 = datetime.strptime(msg.text.split(" - ")[0], "%d.%m.%Y"), "day_to_day"
        date2 = datetime.strptime(msg.text.split(" - ")[1], "%d.%m.%Y")
    else:
        return await msg.reply("Неверный формат даты.")
    await state.finish()
    signals = await db.get.signals()
    signals = list(filter(lambda x: date1[0] <= x.date <= date2 and x.spread > 0, signals))
    if not signals:
        return await msg.reply("Сигналов за указаное время не найдено")
    match date1[1]:
        case "year":
            date1 = date1[0]
            match data["button"]:
                case 10:
                    text = f"Средний спред за {date1.year} год: {round(sum([signal.spread for signal in signals]) / len(signals), 2)}%"
                case 11:
                    text = f"Самый высокий спред за {date1.year} год: {max(signals, key=lambda x: x.spread).spread}%"
                case 12:
                    text = f"За {date1.year} найдено связок: {len(signals)}"
        case "month":
            date1 = date1[0]
            match data["button"]:
                case 10:
                    text = f"Средний спред за {date1.month}.{date1.year}: {round(sum([signal.spread for signal in signals]) / len(signals), 2)}%"
                case 11:
                    text = f"Самый высокий спред за {date1.month}.{date1.year}: {max(signals, key=lambda x: x.spread).spread}%"
                case 12:
                    text = f"За {date1.month}.{date1.year} найдено связок: {len(signals)}"                
        case "day":
            date1 = date1[0]
            match data["button"]:
                case 10:
                    text = f"Средний спред за {date1.day}.{date1.month}.{date1.year}: {round(sum([signal.spread for signal in signals]) / len(signals), 2)}%"
                case 11:
                    text = f"Самый высокий спред за {date1.day}.{date1.month}.{date1.year}: {max(signals, key=lambda x: x.spread).spread}%"
                case 12:
                    text = f"За {date1.day}.{date1.month}.{date1.year} найдено связок: {len(signals)}"
        case "day_to_day":
            date1 = date1[0]
            match data["button"]:
               case 10:
                   text = f"Средний спред за период с {date1.day}.{date1.month}.{date1.year} до {date2.day}.{date2.month}.{date2.year}: {round(sum([signal.spread for signal in signals]) / len(signals), 2)}%"
               case 11:
                   text = f"Самый высокий спред за период с {date1.day}.{date1.month}.{date1.year} до {date2.day}.{date2.month}.{date2.year}: {max(signals, key=lambda x: x.spread).spread}%"
               case 12:
                    text = f"За период с {date1.day}.{date1.month}.{date1.year} до {date2.day}.{date2.month}.{date2.year} найдено связок: {len(signals)}" 
    await msg.reply(text)



async def load(dp: aiogram.Dispatcher):
    dp.register_message_handler(admins_, commands=["admins"])
    dp.register_message_handler(give_signal_, commands=["give_signal"])
    dp.register_callback_query_handler(gsign_buttons_, Text(startswith="give_signal_"))
    dp.register_message_handler(give_user_id_, state=states.Uid.user_id)
    dp.register_message_handler(stats_, commands=["stats"])
    dp.register_callback_query_handler(stats_but_, Text(startswith="stats_"), state="*")
    dp.register_message_handler(input_date, state=states.Stats.date)