from datetime import datetime
import asyncio
import os

import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from buttons import get_signal as kb, start
from utils import database as db
from utils import states

from utils.signals.algorithm import get_orders
from main import SIGNALS

text_signal = """
🚨Спред: {spread}%

{step1}
{step2}
{step3}

_____________________________________
<u>Обязательно проверяйте курсы и комиссии перед использованием связки!</u>
id{id}
"""

text_step = """
💰<b><a href=\"{owner_link}\">{market_name}</a></b> {currency}:{currency2} (Курс: {rate}){banks}
Отдаем {count} {currency}
Получаем {count2} {currency2}{limits}
"""

async def get_signal_(msg: types.Message):
    user = await db.check(user_id=msg.chat.id)
    settings = await db.get.settings()
    await msg.edit_text(settings.getsign_msg, reply_markup=await kb.paymethods(user.user_id, user.paymethods, user.balance))

async def setpaymethod_button_(call: types.CallbackQuery):
    user_id = int(call.data.replace("setpaymethod:", ""))
    if call.from_user.id != user_id:
        return await call.answer("Эта кнопка не для вас.", show_alert=True)
    await get_signal_(call.message)

async def paymethod_(call: types.CallbackQuery, time: datetime = None, lasttext: str = None, new_signal: bool = False, state: FSMContext = None):
    name, user_id, status = call.data.replace("paymethod_", "").split(":")
    user_id, status, user = int(user_id), int(status), await db.check(user_id=user_id)
    settings = await db.get.settings()
    if call.from_user.id != user_id:
        return await call.answer("Эта кнопка не для вас.", show_alert=True)
    if name == "continue":
        if not max([int(i.split(":")[1]) for i in user.paymethods]) or not user.balance:
            return await call.message.answer(settings.setpaymethod_msg, reply_markup=await start.setpaymethod(user_id))
        elif not datetime.now() < user.subscribe and not user.signal:
            return await call.message.answer(settings.suborsign_msg, reply_markup=await start.suborsign(user_id))
        if new_signal:
            await call.message.edit_reply_markup()
            call.message = await call.message.answer("Пожалуйста подождите, обновляем котировки..")
            signals = await db.get.signals(user.user_id)
            if not signals or (len(signals) == 1 and signals[0].id == int(lasttext.split("id")[-1])):
                signals = await db.add.signals((await get_orders()).get_signals(paymethods=user.paymethods, balance=user.balance), user)
            if signals[0].id == int(lasttext.split("id")[-1]):
                del signals[0]
        else:
            await call.message.answer(f"Пожалуйста подождите, обновляем котировки..")
            signals = await db.add.signals((await get_orders()).get_signals(paymethods=user.paymethods, balance=user.balance), user)
        if not signals or signals[0].spread < 0:
            time = time if time else datetime.now()
            lasttext = lasttext if lasttext else call.message.html_text
            await call.message.answer(f"Пожалуйста подождите, обновляем котировки (прошло: {int((datetime.now() - time).total_seconds() // 60)}м)...", reply_markup=await kb.signal(user_id, 0, 'menu'))
            await asyncio.sleep(60)
            return await paymethod_(call, time, lasttext)
        text = []
        for i in range(3):
            text.append(text_step.format(
                owner_link = signals[0].steps[i].owner_link,
                market_name = signals[0].steps[i].market_name,
                currency = signals[0].steps[i].currency if i in [0,1] else signals[0].steps[i].cryptocurrency.upper(),
                currency2 = signals[0].steps[i].cryptocurrency if i in [0,1] else signals[0].steps[i].currency.upper(),
                rate = signals[0].steps[i].rate,
                banks = "" if i == 1 else f"\nБанки: {', '.join([bank for bank in signals[0].steps[i].paymethod if bank.lower() in [paymeth.split(':')[0].lower() for paymeth in user.paymethods if int(paymeth.split(':')[1])]])}",
                count = round(user.balance if i==0 else (user.balance/signals[0].steps[0].price if i==1 else user.balance/signals[0].steps[0].price*signals[0].steps[1].price), 3),
                count2 = round(user.balance/signals[0].steps[0].price if i==0 else (user.balance/signals[0].steps[0].price*signals[0].steps[1].price if i==1 else user.balance/signals[0].steps[0].price*signals[0].steps[1].price*signals[0].steps[2].price), 3),
                limits = "" if i == 1 else f"\n<i>Лимиты {signals[0].steps[i].limit.get('min')} - {signals[0].steps[i].limit.get('max')}</i>"         
            ))
        text = text_signal.format(
            spread = signals[0].spread, 
            step1 = text[0], 
            step2 = text[1],
            step3 = text[2],
            id = signals[0].id
        )
        if user.subscribe < datetime.now():
            if user.signal_free:
                await db.edit.users(user_id, signal_free="signal_free-1")
            else:
                await db.edit.users(user_id, signal="signal-1")
        await call.message.answer(text, reply_markup=await kb.signal(user_id, datetime.now() < user.subscribe), disable_web_page_preview=True)
        msg = await call.message.answer("🔔 Сигнал найден!")
        await asyncio.sleep(60)
        await msg.delete()
    elif name == "balance":
        await state.set_state(states.SetBalance.balance.state)
        await state.update_data(message=call.message)
        return await call.message.answer(f"Баланс сейчас {user.balance}₽. Если вы хотите изменить баланс напишите новый баланс (например 100.0 или 100).", reply_markup=await kb.setbalance(user_id))
    else:
        for i in range(len(user.paymethods)):
            iname, istatus = user.paymethods[i].split(":")
            if name == iname:
                if int(istatus):
                    user.paymethods[i] = f"{iname}:0"
                else:
                    user.paymethods[i] = f"{iname}:1"
        await db.edit.users(user_id, paymethods=f"'{'_#_'.join(user.paymethods)}'")
        return await get_signal_(call.message)

async def setbalance_(msg: types.Message, state: FSMContext):
    newbalance = msg.text.replace(",", ".", 1)
    data = await state.get_data()
    if not newbalance.replace(".", "", 1).isdigit():
        await state.set_state(states.SetBalance.balance.state)
        return await data.get("message").answer("Вы написали сумму в неправильном формате!\nЗаново введите ее (например 100.0 или 100).", reply_markup=await kb.setbalance(msg.from_user.id))
    user = await db.edit.users(msg.from_user.id, balance=float(newbalance))
    await state.finish()
    return await get_signal_(data.get("message"))

async def setbalance_buttons_(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != int(call.data.split("_")[2]):
        return await call.answer("Эта кнопка не для вас.", show_alert=True)
    await state.finish()
    return await get_signal_(call.message)

async def get_all_signals(msg: types.Message):
    if not msg.get_args():
        return await msg.reply("Пожалуйста введите команду в формате\n/all_signals {сумма}")
    if not msg.get_args().replace(",", ".", 1).replace(".", "", 1).isdigit():
        return await msg.reply("Сумма введена не в правильном формате!\nпримеры: 100 | 100.5 | 100,5")
    balance = float(msg.get_args().replace(",", "."))
    orders = await get_orders()
    signals = sorted(await db.add.signals(orders.get_signals(['Tinkoff:1','SberBank:1','QIWI:1','YooMoney:1','AlfaBank:1','Payeer:1'], balance), await db.get.users(user_id=msg.from_user.id)), key=lambda x: x.spread, reverse=True)
    with open(f'all_signals_ball{balance}.txt', 'w+') as file:
        file.write("Сигналы:")
        for signal in signals:
            file.write(f"\n\n    спред: {signal.spread}%")
            c = 0
            for i in range(len(signal.steps)):
                file.write(f"\n    {signal.steps[i].owner_link} {signal.steps[i].market_name} {signal.steps[i].currency if c in [0,1] else signal.steps[i].cryptocurrency}:{signal.steps[i].cryptocurrency if c in [0,1] else signal.steps[i].currency} (Курс: {signal.steps[i].rate})")
                if signal.steps[i].market_name not in ["Binance"]:
                    file.write(f"\n    Банки: {', '.join(signal.steps[i].paymethod)}")
                file.write(f"\n    Отдаем {balance if i==0 else (balance/signal.steps[0].price if i==1 else balance/signal.steps[0].price*signal.steps[1].price)} {signal.steps[i].currency if c in [0,1] else signal.steps[i].cryptocurrency}")
                file.write(f"\n    Получаем {balance/signal.steps[0].price if i==0 else (balance/signal.steps[0].price*signal.steps[1].price if i==1 else balance/signal.steps[0].price*signal.steps[1].price*signal.steps[2].price)} {signal.steps[i].cryptocurrency if c in [0,1] else signal.steps[i].currency}")
                if signal.steps[i].market_name not in ["Binance"]:
                    file.write(f"\n    Лимиты {signal.steps[i].limit.get('min')} - {signal.steps[i].limit.get('max')}")
                c += 1
    with open(f'all_orders_ball{balance}.txt', 'w+') as file:
        file.write("Ордера:")
        for order in orders._buy + orders._sell + orders._ctc:
            file.write(f"\n\n    биржа: {order.market_name}")
            file.write(f"\n    Ссылка на человека: {order.owner_link}")
            file.write(f"\n    Цена: {order.price}")
            file.write(f"\n    Банки: {', '.join(order.paymethod)}")
            file.write(f"\n    Лимиты: мин - {order.limit.get('min') if order.limit else 'нет'}; макс - {order.limit.get('max') if order.limit else 'нет'}")
            file.write(f"\n    Валюты: {order.currency}; {order.cryptocurrency}")
    with open(f'all_signals_ball{balance}.txt', 'rb') as file:
        await msg.reply_document(file)
    with open(f'all_orders_ball{balance}.txt', 'rb') as file:
        await msg.reply_document(file)
    os.remove(f'all_signals_ball{balance}.txt')
    os.remove(f'all_orders_ball{balance}.txt')

async def get_all_orders(msg: types.Message):
    orders = await get_orders()
    with open(f'all_orders.txt', 'w+') as file:
        file.write("Ордера:")
        for order in orders._buy + orders._sell + orders._ctc:
            file.write(f"\n\n    биржа: {order.market_name}")
            file.write(f"\n    Ссылка на человека: {order.owner_link}")
            file.write(f"\n    Цена: {order.price}")
            file.write(f"\n    Банки: {', '.join(order.paymethod)}")
            file.write(f"\n    Лимиты: мин - {order.limit.get('min') if order.limit else 'нет'}; макс - {order.limit.get('max') if order.limit else 'нет'}")
            file.write(f"\n    Валюты: {order.currency}; {order.cryptocurrency}")
    with open(f'all_orders.txt', 'rb') as file:
        await msg.reply_document(file)
    os.remove('all_orders.txt')



async def load(dp: aiogram.Dispatcher):
    dp.register_callback_query_handler(setpaymethod_button_, Text(startswith="setpaymethod:"))
    dp.register_callback_query_handler(paymethod_, Text(startswith="paymethod_"))
    dp.register_callback_query_handler(setbalance_buttons_, Text(startswith="setbalance_"), state="*")
    dp.register_message_handler(setbalance_, state=states.SetBalance.balance)
    dp.register_message_handler(get_all_signals, commands=["all_signals"])
    dp.register_message_handler(get_all_orders, commands=["all_orders"])