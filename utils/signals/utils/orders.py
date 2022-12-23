import asyncio

from typing import Any, Generator

from ..api import get_orders_data
from ..api.binance import BinanceP2P, Binance
from ..api.bitzlato import BitzlatoP2P, Bitzlato
from ..api.bitpapa import BitpapaP2P
from ..api.huabi import HuobiP2P, Huobi
from ..api.okx import OkxP2P, Okx
from ..api.totalcoin import TotalcoinP2P
from ..api.bybit import BybitP2P, Bybit
from ..api.garantex import Garantex
from .data import Order
from ..algorithm.logic import OrderSet



Exchanger = TotalcoinP2P | HuobiP2P | OkxP2P | BitpapaP2P | BinanceP2P | BitzlatoP2P | BybitP2P
BUY = Order
SELL = Order
Orders = tuple




async def _get_orders_by_type(exchange: Exchanger, type: str) -> list[Order]:
    """Getting orders by specific type.

    Args:
        exchange (Exchanger): An instance or object of Exchanger
        type (str): BUY or SELL

    Returns:
        list[Order]: A list with orders data
    """
    orders = []
    if isinstance(exchange, TotalcoinP2P):
        cryptocurrs = ('BTC',)
    elif isinstance(exchange, (OkxP2P, HuobiP2P, BitpapaP2P, BybitP2P)):
        cryptocurrs = ('USDT', 'ETH', 'BTC')
    elif isinstance(exchange, BitzlatoP2P):
        cryptocurrs = ('USDT', 'ETH', 'BTC', 'DOGE')
    else:
        cryptocurrs = ('USDT', 'ETH', 'BTC', 'BUSD', 'BNB')

    if exchange.__class__.__name__ == "Binance":
        orders_generator = get_orders_data(exchange, None, "BUY", None)
        async for order in orders_generator:
            if order:
                orders.append(order)
        
        return orders

    types = {
        "BUY": "SELL",
        "SELL": "BUY"
    }
    reverse_type = ["OkxP2P", "HuobiP2P"]
    type = type if exchange.__class__.__name__ not in reverse_type else types[type]
    for crypto in cryptocurrs:
        orders_generator = get_orders_data(exchange, trade_type=type, cryptocurrency=crypto)
        async for order in orders_generator:
            if order:
                orders.append(order)

    return orders


def _collect_tasks() -> Generator[Orders[BUY, SELL], Any, Any]:
    """Collecting tasks to start it in parallel

    Returns:
        Orders[BUY, SELL]: An orders generators with buy and sell data
    """
    tasks_buy_type, tasks_sell_type, tasks_crypt_to_crypt = set(), set(), set()
    for exchange in (BinanceP2P(), OkxP2P(), TotalcoinP2P(), BitpapaP2P()): #, BybitP2P(), BitzlatoP2P(), HuobiP2P()):
        tasks_buy_type.add(asyncio.create_task(_get_orders_by_type(exchange=exchange, type='BUY')))
        tasks_sell_type.add(asyncio.create_task(_get_orders_by_type(exchange=exchange, type='SELL')))
    for exchange in (Bitzlato(), Binance(), Bybit(), Okx(), Garantex()): #, Huobi()):
        tasks_crypt_to_crypt.add(asyncio.create_task(_get_orders_by_type(exchange, None)))

    ctc = asyncio.as_completed(tasks_crypt_to_crypt)
    buy = asyncio.as_completed(tasks_buy_type)
    sell = asyncio.as_completed(tasks_sell_type)

    return buy, sell, ctc

async def get_orders() -> OrderSet:
    """Getting ordersset

    Returns:
        OrderSet: creates an OrderSet instance with data.
    """
    buy_orders, sell_orders, ctc_orders = _collect_tasks()
    buy, sell, ctc = [], [], []
    for b_ords in buy_orders:
        orders = await b_ords
        buy += orders
    for s_ords in sell_orders:
        orders = await s_ords
        sell += orders
    for c_orders in ctc_orders:
        orders = await c_orders
        ctc += orders
    return OrderSet(buy, sell, ctc)
    