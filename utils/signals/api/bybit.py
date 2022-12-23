import logging
import requests

from locale import currency
import websocket
import json
from typing import NoReturn

from .base import BaseP2P
from ..async_requester import AsyncRequest
from ..utils.data import Order

PAYMETHOD = {
    51: "Payeer",
    75: "Tinkoff",
    62: "QIWI",
    377: "SberBank",
    379: "AlfaBank",
    274: "YooMoney"
}

DEF_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'

class BybitP2P(BaseP2P):
    
    def __init__(self) -> None:
        super().__init__()
        self._api = 'https://api2.bybit.com/spot/api/otc/item/list'
        self.ss = requests.Session()
        
        
    async def get_orders(
        self: 'BybitP2P', 
        currency: str, 
        cryptocurrency: str, 
        trade_type: str = 'BUY'
        ) -> list[dict] | None | NoReturn:
        currency = currency.upper()
        trade_type = trade_type.upper()
        cryptocurrency = cryptocurrency.upper()

        if not isinstance(trade_type, str):
            raise TypeError(f'trade_type must be str, not {type(trade_type).__name__}')
        if trade_type.upper() not in ('BUY', 'SELL'):
            raise ValueError(f'trade_type must be BUY or SELL, not {type(trade_type).__name__}') 

        data = {
            "tokenId": cryptocurrency,
            "currencyId": currency,
            "side": '1' if trade_type == "BUY" else '0',
            "size": '20',
            "page": '1'
        }

        self.ss.headers['Content-Type'] = 'application/json'
        self.ss.headers['charset'] = 'utf-8'
        self.ss.headers['User-Agent'] = DEF_UA

        response = requests.get(self._api, params=data)
        if (data := response.json()) and data.get('result'):
            return data.get('result').get("items")
        else:
            logging.warning(f"Bybit P2P return {response.status_code} code;  cc: {cryptocurrency}; c: {currency}; td: {trade_type}")
      
    
    async def get_order_data(self, order: dict) -> Order | NoReturn:
        
        if not isinstance(order, dict):
            raise TypeError(f'order must be a dictionary, not {type(order).__name__}')
        price = float(order["price"])
        limit = {
            "min": float(order["minAmount"]),
            "max": float(order["maxAmount"])
        }
        owner = order["nickName"]
        paymethod_ids = order["payments"]
        paymethod = [ii for i in order["payments"] if (ii := PAYMETHOD.get(i))]
        trade_type = "BUY" if int(order["side"]) == 1 else "SELL"
        trade_type_id = order["side"]

        match trade_type:
            case 'SELL':
                rate = f"{price}:1"
                return Order(
                    market_name=self.__class__.__name__,
                    currency=order["currencyId"],
                    cryptocurrency=order["tokenName"],
                    exchange="",
                    owner_link=f"https://www.bybit.com/fiat/trade/otc/?actionType={trade_type_id}&token={order['tokenName']}&fiat={order['currencyId']}",
                    owner=owner,
                    rate=rate,
                    price=price,
                    limit=limit,
                    paymethod=paymethod,
                    paymethod_id=paymethod_ids
                )
             
            case 'BUY':
                rate = f"1:{price}"
                return Order(
                    market_name=self.__class__.__name__,
                    currency=order["currencyId"],
                    cryptocurrency=order["tokenName"],
                    exchange="",
                    owner_link=f"https://www.bybit.com/fiat/trade/otc/?actionType={trade_type_id}&token={order['tokenName']}&fiat={order['currencyId']}",
                    owner=owner,
                    rate=rate,
                    price=price,
                    limit=limit,
                    paymethod=paymethod,
                    paymethod_id=paymethod_ids
                )

class Bybit(BaseP2P):
    __slots__ = ('_api', 'currency', 'cryptocurrency')
    
    def __init__(self) -> None:
        super().__init__()
        self._api = 'https://api.bybit.com/spot/v3/public/quote/ticker/24hr'
        
        
    async def get_orders(
        self: 'Bybit', 
        currency: str, 
        cryptocurrency: str, 
        trade_type: str = 'BUY'
        ) -> list[dict] | None | NoReturn:

        crypts = ('USDT','ETH', 'BTC', 'BUSD', 'BNB')
        self._session.headers['Content-Type'] = 'application/json'
        response = await self._session.get(self._api, json_data=True)
        if (data := response.content):
            res = []
            for i in crypts:
                for i2 in crypts:
                    res.append(i+i2)
            data = [i for i in data["result"]["list"] if i["s"] in res]
            return data
      
    
    async def get_order_data(self, order: dict) -> Order | NoReturn:
        
        if not isinstance(order, dict):
            raise TypeError(f'order must be a dictionary, not {type(order).__name__}')
        
        crypts = ('USDT','ETH', 'BTC', 'BUSD', 'BNB')
        for i in range(len(order['s'])):
            if order['s'][:i] in crypts:
                crypt1 = order['s'][:i]
                crypt2 = order['s'][i:]
        
        return Order(
            market_name=self.__class__.__name__,
            currency=crypt1,
            cryptocurrency=crypt2,
            exchange="",
            owner_link=f"https://www.bybit.com/ru-RU/trade/spot/{crypt1}/{crypt2}",
            owner=None,
            rate=f"1:{order['o']}",
            price=float(order['o']),
            limit=None,
            paymethod=[],
            paymethod_id=[]
        )