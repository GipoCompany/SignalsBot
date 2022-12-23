from locale import currency
import websocket
import json
from typing import NoReturn

from .base import BaseP2P
from ..async_requester import AsyncRequest
from ..utils.data import Order


class BinanceP2P(BaseP2P):
    
    __slots__ = ('_api', 'currency', 'cryptocurrency')
    
    def __init__(self) -> None:
        super().__init__()
        self._api = 'https://c2c.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
        
        
    async def get_orders(
        self: 'BinanceP2P', 
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
            'page': 1,
            'rows': 10,
            'countries': [],
            'publisherType': None, 
            'proMerchantAds': False, 
            'tradeType': trade_type, 
            'fiat': currency,
            'asset': cryptocurrency,
            'payTypes': [],       
        }
        self._session.headers['Content-Type'] = 'application/json'
        
        response = await self._session.post(self._api, json_data=True, data=json.dumps(data, ensure_ascii=False))
       
        if (data := response.content):
            return data.get('data')
      
    
    async def get_order_data(self, order: dict) -> Order | NoReturn:
        
        if not isinstance(order, dict):
            raise TypeError(f'order must be a dictionary, not {type(order).__name__}')
        
        trade_type = order['adv']['tradeType']
        min_single_trans_quantity = order['adv']['minSingleTransQuantity']
        max_single_trans_quantity = order['adv']['maxSingleTransQuantity']
        
        dynamic_max_single_trans_quantity = order['adv']['dynamicMaxSingleTransQuantity']
        
        min_single_trans_amount = order['adv']['minSingleTransAmount']
        max_single_trans_amount = order['adv']['maxSingleTransAmount']
        
        dynamic_max_single_trans_amount = order['adv']['dynamicMaxSingleTransAmount']
        
        owner = order['advertiser']['nickName']
        owner_link = f"https://p2p.binance.com/ru-UA/advertiserDetail?advertiserNo={order['advertiser']['userNo']}"
        paymethod = [method['tradeMethodName'] for method in order['adv']['tradeMethods']]
        paymethod_ids = [method.get('payMethodId') for method in order['adv']['tradeMethods']]
        
        _limit = {
                    'quantity': {
                        'dynamic': {
                            'max': float(dynamic_max_single_trans_quantity) 
                        },
                        'single': {
                            'min': float(min_single_trans_quantity),
                            'max': float(max_single_trans_quantity)
                        }
                    },
                    'amount': {
                        'dynamic':{
                            'max': float(dynamic_max_single_trans_amount)
                        },
                        'single': {
                            'min': float(min_single_trans_amount),
                            'max': float(max_single_trans_amount)
                        }
                    }  
                }
        limit = {
            'min': float(min_single_trans_amount),
            'max': float(max_single_trans_amount)
        }
        price = float(order['adv']['price'])
        exchange = 'https://www.binance.com'
        match trade_type:
            case 'SELL':
                rate = f"{price}:1"
                return Order(
                    market_name=self.__class__.__name__,
                    currency=order["adv"]["fiatUnit"],
                    cryptocurrency=order["adv"]["asset"],
                    exchange=exchange,
                    owner_link=owner_link,
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
                    currency=order["adv"]["fiatUnit"],
                    cryptocurrency=order["adv"]["asset"],
                    exchange=exchange,
                    owner_link=owner_link,
                    owner=owner,
                    rate=rate,
                    price=price,
                    limit=limit,
                    paymethod=paymethod,
                    paymethod_id=paymethod_ids
                )
# Not sure about this class, need tests
#class Binance:
#    
#    __slots__ = ('_api', '_session')
#    
#    def __init__(self) -> None:
#        
#        self._api = 'https://www.binance.com/ru/trade/BTC_USDT?theme=dark&type=spot'
#        self._session = AsyncRequest(step=50)
#    
#    
#    async def get_currencies(self: 'Binance') -> list[dict] | NoReturn:
#        
#        response = await self._session.get(self._api)
#        item_data = await response.html.select_one('script#__APP_DATA')
#        
#        if item_data:
#            data = json.loads(item_data.get_text(strip=True))
#            return data["pageData"]["redux"]["pageStore"]["currency"]
#        
#        raise ValueError(f"Expected site data, got {type(item_data).__name__}")
#    
#    @staticmethod
#    async def get_course(left_currency: str, right_currency: str) -> str | NoReturn:
#        
#        if not all([isinstance(left_currency, str), isinstance(right_currency, str)]):
#            raise TypeError(f'Expected str, got {type(left_currency).__name__}/{type(right_currency).__name__}')
#        
#        currency_pair = (right_currency + left_currency).lower()
#        binance_ws = websocket.create_connection(f"wss://stream.binance.com:9443/ws/{currency_pair}@aggTrade")
#        response = binance_ws.recv()
#        binance_ws.close()     
#        
#        course = float(json.loads(response)['p'])
#        if course < 1:
#            return f'{1 / course}:1'
#        
#        return f'1:{course}'
        

class Binance(BaseP2P):
    __slots__ = ('_api', 'currency', 'cryptocurrency')
    
    def __init__(self) -> None:
        super().__init__()
        self._api = 'https://api.binance.com/api/v3/ticker/price'
        
        
    async def get_orders(
        self: 'BinanceP2P', 
        currency: str, 
        cryptocurrency: str, 
        trade_type: str = 'BUY'
        ) -> list[dict] | None | NoReturn:

        crypts = ('USDT','ETH', 'BTC', 'BUSD', 'BNB')
        self._session.headers['Content-Type'] = 'application/json'
        response = await self._session.get(self._api, json_data=True)
        if (data := response.content):
            data = [i for i in data if i['symbol'] in [crypt1+crypt2 for crypt1 in crypts for crypt2 in crypts]]
            for i in range(len(data)):
                for j in range(len(data[i]['symbol'])):
                    if data[i]['symbol'][:j] in crypts:
                        price = str(1/float(data[i]['price']))
                        data.append({'symbol': data[i]['symbol'][j:]+data[i]['symbol'][:j], 'price': price})
            return data
      
    
    async def get_order_data(self, order: dict) -> Order | NoReturn:
        
        if not isinstance(order, dict):
            raise TypeError(f'order must be a dictionary, not {type(order).__name__}')
        
        crypts = ['USDT', 'ETH', 'BTC', 'BUSD', 'BNB']
        for i in range(len(order['symbol'])):
            if order['symbol'][:i] in crypts:
                crypt1 = order['symbol'][:i]
                crypt2 = order['symbol'][i:]
        owner_link = f"https://www.binance.com/ru/trade/{crypt1}_{crypt2}?theme=dark&type=spot"
        price = float(order['price'])
        exchange = 'https://www.binance.com'
        rate = f"1:{price}"
        return Order(
            market_name=self.__class__.__name__,
            currency=crypt1,
            cryptocurrency=crypt2,
            exchange=exchange,
            owner_link=owner_link,
            owner=None,
            rate=rate,
            price=price,
            limit=None,
            paymethod=[],
            paymethod_id=[]
        )