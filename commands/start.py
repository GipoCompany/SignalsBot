from tracemalloc import start
import aiogram
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from datetime import datetime

from commands.get_signal import get_signal_, paymethod_
from buttons import start as kb
from utils import database as db
from utils import states

async def start_(msg: types.Message, state: FSMContext, first=True, user_id=None):
    if state:
        await state.finish()
    settings = await db.get.settings()
    if not first:
        user = await db.check(user_id=user_id)
        return await msg.answer(settings.start_msg, reply_markup=await kb.main(user_id=user_id))
    user = await db.check(msg)
    await msg.reply(settings.start_msg, reply_markup=await kb.main(user_id=msg.from_user.id))

async def start_buttons_(call: types.CallbackQuery):
    button, user_id = call.data.replace("start_", "").split(":")
    user_id, user = int(user_id), await db.check(call)
    settings = await db.get.settings()
    if call.from_user.id != user_id:
        return await call.answer("Эта кнопка не для вас.", show_alert=True)
    if button == "using":
        await call.message.answer(settings.using_msg, reply_markup=await kb.using(user_id))
    if button == "getsign":
        if datetime.now() > user.subscribe and not user.signal:
            return await call.message.answer(settings.suborsign_msg, reply_markup=await kb.suborsign(user_id))
        elif not max([int(i.split(":")[1]) for i in user.paymethods]) or not user.balance:
            return await call.message.answer(settings.setpaymethod_msg, reply_markup=await kb.setpaymethod(user_id))
        else:
            return await get_signal_(call.message)

async def using_(call: types.CallbackQuery):
    if call.from_user.id != int(call.data.replace("using_back:", "")):
        return await call.answer("Эта кнопка не для вас.", show_alert=True)
    await start_(call.message, None, False, int(call.data.replace("using_back:", "")))

async def suborsign_(call: types.CallbackQuery):
    button, user_id = call.data.replace("suborsign_", "").split(":")
    settings, user = await db.get.settings(), await db.get.users(user_id=user_id)
    if call.from_user.id != int(user_id):
        return await call.answer("Эта кнопка не для вас.", show_alert=True)
    if button == "menu":
        await start_(call.message, None, False, user_id)
    if button == "buysub":
        price = settings.buysub_price if user.subscribe_count > 25 else settings.first_buysub_price
        await call.message.answer(settings.buysub_msg.format(price=price, walletTRC20=settings.walletTRC20, walletBEP20=settings.walletBEP20), reply_markup=await kb.buy(user_id, price, "sub"))
    if button == "buysign":
        await call.message.answer(settings.buysign_msg.format(price=settings.buysign_price, walletTRC20=settings.walletTRC20, walletBEP20=settings.walletBEP20), reply_markup=await kb.buy(user_id, settings.buysign_price, "sign"))

async def signal_(call: types.CallbackQuery):
    button, user_id = call.data.replace("signal_", "").split(":")
    user = await db.get.users(user_id=user_id)
    if call.from_user.id != int(user_id):
        return await call.answer("Эта кнопка не для вас.", show_alert=True)
    if button == "menu":
        await start_(call.message, None, False, user_id)
    elif button == "dontuse":
        if not user.reserve_signal:
            return await call.answer("В этом месяце вы уже использовали 3/3 сигналов.", show_alert=True)
        await db.edit.users(user_id, signal="signal+1", reserve_signal="reserve_signal-1")
        return await get_signal_(call.message)
    elif button == "newsignal":
        if datetime.now() > user.subscribe and not user.signal:
            call.data = f"start_getsign:{user_id}"
            return await start_buttons_(call)
        call.data = f"paymethod_continue:{user_id}:0"
        return await paymethod_(call, None, call.message.html_text, True)

async def load(dp: aiogram.Dispatcher):
    dp.register_message_handler(start_, commands=["start"], state="*")
    dp.register_callback_query_handler(start_buttons_, Text(startswith="start_"))
    dp.register_callback_query_handler(suborsign_, Text(startswith="suborsign_"))
    dp.register_callback_query_handler(using_, Text(startswith="using_"))
    dp.register_callback_query_handler(signal_, Text(startswith="signal_"))
