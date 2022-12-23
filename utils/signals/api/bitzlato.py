import requests
import json
from ..utils.data import Order
from .base import BaseP2P
import logging

DEF_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'


class BitzlatoP2P(BaseP2P):
    
    def __init__(self):
        self._api = 'https://bitzlato.bz'
        self.ss = requests.Session()
        self.ss.headers.update({'User-Agent': DEF_UA})
        
    async def get_orders(
        self: 'BitzlatoP2P',
        currency: str, 
        cryptocurrency: str,
        trade_type: str) -> list[dict] | None:
        
        trade_type = 'purchase' if trade_type == 'BUY' else 'selling'

        params = {
            'limit': 15, 
            'skip': 0, 
            'type': trade_type, 
            'lang': 'ru',
            'isOwnerVerificated': 'true', 
            'isOwnerTrusted': 'false', 
            'isOwnerActive': 'false',
            'currency': currency, 
            'cryptocurrency': cryptocurrency
        }
      
        result = self.ss.get(self._api + '/api2/p2p/public/exchange/dsa/', params=params)
        
        result_obj = json.loads(result.text)
        
        return result_obj['data'] if result_obj.get('total') else logging.warning(f"Bitzlato P2P return {result.status_code} code;  cc: {cryptocurrency}; c: {currency}; td: {trade_type}")
    
    async def get_order_data(self, order: dict) -> Order:
        
        trade_type = order['type']
        _limit = order['limitCurrency']
        second_limit = order['limitCryptocurrency']
        owner = order['owner']
        owner_link = f'{self._api}/p2p/users/{owner}'
        paymethod = (order['paymethod']['name'],)
        paymethod_id = order['paymethodId']
        price = float(order["rate"])
        limit_ = {
            'currency': {
                'min': float(_limit['min']),
                'max': float(_limit['max']),
            },
            'cryptocurrency': {
                'min': float(second_limit['min']),
                'max': float(second_limit['max']),
            }
        }
        limit = {
            'min': float(_limit['min']),
            'max': float(_limit['max'])
            }
        match trade_type:
            case 'selling':
                rate = f'{order["rate"]}:1'
                return Order(
                    market_name=self.__class__.__name__,
                    currency=order["currency"],
                    cryptocurrency=order["cryptocurrency"],
                    exchange=self._api,
                    owner_link=owner_link,
                    owner=owner,
                    rate=rate,
                    limit=limit,
                    paymethod=paymethod,
                    paymethod_id=paymethod_id,
                    price=price
                )

            case 'purchase':
                rate = f'1:{order["rate"]}'
                return Order(
                    market_name=self.__class__.__name__,
                    currency=order["currency"],
                    cryptocurrency=order["cryptocurrency"],
                    exchange=self._api,
                    owner_link=owner_link,
                    owner=owner,
                    rate=rate,
                    limit=limit,
                    paymethod=paymethod,
                    paymethod_id=paymethod_id,
                    price=price
                )

class Bitzlato(BaseP2P):
    
    def __init__(self) -> None:
        super().__init__()
        self._api = 'https://bitzlato.net/api/v2/peatio/public/markets/tickers'
        self.ss = requests.Session()
        self.ss.headers.update({'User-Agent': DEF_UA})
        
        
    async def get_orders(
        self: 'Bitzlato', 
        currency: str, 
        cryptocurrency: str, 
        trade_type: str = 'BUY'
        ) -> list[dict] | None:

        crypts = ('USDT','ETH', 'BTC', 'BUSD', 'BNB')
        result = self.ss.get(self._api)
        result_ = json.loads(result.text)
        return filter(lambda x: x[0].split("_")[0].upper() in crypts and x[0].split("_")[1].upper() in crypts, result_.items()) if result.status_code == 200 else logging.warning(f"Bitzlato spot return {result.status_code} code")
      
    
    async def get_order_data(self, order: dict) -> Order:
        
        if not isinstance(order, dict | tuple | list):
            raise TypeError(f'order must be a dictionary, not {type(order).__name__}')
        
        crypt1, crypt2 = [i.upper() for i in order[0].split("_")]
        
        return Order(
            market_name=self.__class__.__name__,
            currency=crypt1,
            cryptocurrency=crypt2,
            exchange="",
            owner_link=f"",
            owner=None,
            rate=f"1:{order[1]['ticker']['avg_price']}",
            price=float(order[1]['ticker']['avg_price']),
            limit=None,
            paymethod=[],
            paymethod_id=[]
        )