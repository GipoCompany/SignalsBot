from typing import AsyncGenerator, Any
import logging
from .binance import BinanceP2P, Binance
from .bitpapa import BitpapaP2P
from .bitzlato import Bitzlato, BitzlatoP2P
from .huabi import HuobiP2P, Huobi
from .okx import OkxP2P, Okx
from .totalcoin import TotalcoinP2P
from .bybit import BybitP2P, Bybit
from .garantex import Garantex
from ..utils.data import Order

__all__ = [
    'get_orders_data',
]


async def get_orders_data(
    obj: BinanceP2P | BitpapaP2P | BitzlatoP2P | Bitzlato | HuobiP2P | Huobi | OkxP2P | Okx | TotalcoinP2P | Binance | BybitP2P | Bybit | Garantex,
    cryptocurrency: str, 
    trade_type: str = "BUY",
    currency: str = 'RUB'
    ) -> AsyncGenerator[Order, Any]:

    if callable(obj):
        cls = obj()
    else:
        cls = obj
        
    orders = await cls.get_orders(currency=currency, cryptocurrency=cryptocurrency, trade_type=trade_type)
    if orders:
        for order in orders:
                yield await obj.get_order_data(order=order)
    else:
        logging.warning(f"{cls.__class__.__name__} no orders; cc: {cryptocurrency}; c: {currency}; td: {trade_type}")
        yield orders
    
# deprecated function
# async def get_orders_data_btc_only(
#     obj: TotalcoinP2P,
#     trade_type: str,
#     currency: str = 'RUB'
#     ) -> AsyncGenerator[Order, Any]:
    
#     if callable(obj):
#         cls = obj()
#     else:
#         cls = obj
        
#     orders = await cls.get_orders(currency=currency, trade_type=trade_type)
#     if orders:
#         for order in orders:
#             yield await obj.get_order_data(order=order)
#     else:
#         yield orders
            