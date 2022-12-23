import logging
import requests

from locale import currency
import websocket
import json
from typing import NoReturn

from .base import BaseP2P
from ..async_requester import AsyncRequest
from ..utils.data import Order

class Garantex(BaseP2P):
    __slots__ = ('_api', 'currency', 'cryptocurrency')
    
    def __init__(self) -> None:
        super().__init__()
        self._api = 'https://garantex.io/api/v2/trades'
        
        
    async def get_orders(
        self: 'Garantex', 
        currency: str, 
        cryptocurrency: str, 
        trade_type: str = 'BUY'
        ) -> list[dict] | None | NoReturn:

        crypts = (("ETH", "BTC"), ("BTC", "USDT"), ("ETH", "USDT"))
        self._session.headers['Content-Type'] = 'application/json'
        res = []
        for i in crypts:
            res_ = await self._session.get(self._api + f"?market={i[0].lower()}{i[1].lower()}", json_data=True)
            if res_.status_code == 200:
                l = res_.content[0]
                l["crypt1"] = i[0]
                l["crypt2"] = i[1]
                res.append(l)
        return res

      
    
    async def get_order_data(self, order: dict) -> Order | NoReturn:
        
        if not isinstance(order, dict):
            raise TypeError(f'order must be a dictionary, not {type(order).__name__}')
        
        crypt1, crypt2 = order['crypt1'], order['crypt2']
        
        return Order(
            market_name=self.__class__.__name__,
            currency=crypt1,
            cryptocurrency=crypt2,
            exchange="",
            owner_link=f"https://garantex.io/trading/{crypt1}{crypt2}",
            owner=None,
            rate=f"1:{order['price']}",
            price=float(order['price']),
            limit=None,
            paymethod=[],
            paymethod_id=[]
        )