from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

import aiogram
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from commands.get_signal import get_signal_
from buttons import start as kb
import buttons
from utils import database as db
import utils.types as mytypes
from utils import states

async def precheck_(call: types.CallbackQuery, state: FSMContext):
    user = await db.get.users(user_id=call.data.replace("buy_", "").split(":")[1])
    if user.wallet:
        return await buy_check_(call)
    await state.update_data(call=call)
    await state.set_state(states.Wallet.wallet.state)
    await call.message.answer("Введите адрес своего кошелька:")

async def reset_wallet_(call: types.CallbackQuery, state: FSMContext):
    call.data = call.data.replace('reset_wallet:', "")
    await state.update_data(call=call)
    await state.set_state(states.Wallet.wallet.state)
    await call.message.answer("Введите адрес своего кошелька:")

async def setwallet_(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if not msg.text.replace(' ', '') in [i.wallet for i in await db.get.users()]:
        await db.edit.users(user_id=msg.from_user.id, wallet=f"'{msg.text.replace(' ', '')}'")
    else:
        await msg.reply("ОШИБКА! похоже адрес этого кошелька уже использует другой пользователь.")  
        await state.set_state(states.Wallet.wallet.state)
        return await msg.answer("Введите адрес своего кошелька:")
    await state.finish()
    await msg.reply("Адрес кошелька записан.")
    await buy_check_(data.get("call"))

async def buy_check_(call: types.CallbackQuery):
    type, user_id, price = call.data.replace("buy_", "").split(":")
    user_id, price, user = int(user_id), float(price), await db.get.users(user_id=user_id)
    settings = await db.get.settings()
    if call.from_user.id != user_id:
        return await call.answer("Эта кнопка не для вас.", show_alert=True)
    try:
        res = [mytypes.Transaction.TRC20(trans) for trans in requests.get(f'https://apilist.tronscanapi.com/api/token_trc20/transfers?sort=-timestamp&count=true&limit=100&start=0&address={user.wallet}&toAddress={settings.walletTRC20}').json()["token_transfers"]]
        if not res:
            raise NameError
    except:
        try:
            res = [mytypes.Transaction.BEP20(trans) for trans in list(filter(lambda x: x["to"] == settings.walletBEP20, requests.get(f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress=0x55d398326f99059ff775485246999027b3197955&address={user.wallet}&page=1&offset=100&startblock=0&endblock=999999999&sort=desc&apikey=M2R67E68XSFMD6UBXKCVHS9ZKCDJ682PRC").json()["result"]))]
            if not res:
                raise NameError
        except:
            await call.message.answer("ОШИБКА! проверьте правильность адреса вашего кошелька и попробуйте еще раз. В случае повторной ошибки сообщите о проблеме.\n\n"+(settings.buysub_msg.format(price=price, walletTRC20=settings.walletTRC20, walletBEP20=settings.walletBEP20) if type=="sub" else settings.buysign_msg.format(price=settings.buysign_price, walletTRC20=settings.walletTRC20, walletBEP20=settings.walletBEP20)), reply_markup=(await kb.buy(user_id, price, type)).add(types.InlineKeyboardButton("Изменить адрес кошелька", callback_data=f"reset_wallet:{user_id}")))
    res = [i for i in res if i.amount == price and user.wallet == i.from_]
    if not res:
        return await call.message.answer("Операций с вашего кошелька не найдено.\n\n"+(settings.buysub_msg.format(price=price, walletTRC20=settings.walletTRC20, walletBEP20=settings.walletBEP20) if type=="sub" else settings.buysign_msg.format(price=settings.buysign_price, walletTRC20=settings.walletTRC20, walletBEP20=settings.walletBEP20)), reply_markup=(await kb.buy(user_id, price, type)).add(types.InlineKeyboardButton("Изменить адрес кошелька", callback_data=f"reset_wallet:{call.data}")))
    if res[0].hash == user.lasthash:
        return await call.message.answer("Хеш последней транзакции с вашего кошелька уже зарегестрирован.\n\n"+(settings.buysub_msg.format(price=price, walletTRC20=settings.walletTRC20, walletBEP20=settings.walletBEP20) if type=="sub" else settings.buysign_msg.format(price=settings.buysign_price, walletTRC20=settings.walletTRC20, walletBEP20=settings.walletBEP20)), reply_markup=(await kb.buy(user_id, price, type)).add(types.InlineKeyboardButton("Изменить адрес кошелька", callback_data=f"reset_wallet:{call.data}")))
    if type == "sign":
        user = await db.edit.users(user_id, signal="signal+1", signal_count="signal_count+1", lasthash=f"'{res[0].hash}'")
    if type == "sub":
        user = await db.edit.users(user_id, subscribe=f"'{(datetime.now() + timedelta(days=30.5)).strftime('%Y-%m-%d %H:%M:%S')}'", subscribe_count="subscribe_count+1", lasthash=f"'{res[0].hash}'")
    if not max([int(i.split(":")[1]) for i in user.paymethods]):
        return await call.message.answer(settings.setpaymethod_msg, reply_markup=await buttons.start.setpaymethod(user_id))
    else:
        return await get_signal_(call.message)


async def load(dp: aiogram.Dispatcher):
    dp.register_callback_query_handler(precheck_, Text(startswith="buy_"))
    dp.register_callback_query_handler(reset_wallet_, Text(startswith="reset_wallet"))
    dp.register_message_handler(setwallet_, state=states.Wallet.wallet)