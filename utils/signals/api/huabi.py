from locale import currency

from utils.signals.algorithm.logic import Crypt
from .base import BaseP2P 
from ..utils.data import Order


CRYPTA = {
    'USDT': 2,
    'BTC': 1,
    'ETH': 3,
    'HT': 4,
    'EOS': 5,
    'XRP': 7,
    'LTC': 8
}
CRYPTA.update({v:k for k,v in CRYPTA.items()})

CURRENCIES = {
    'USD': 2,
    'HKD': 13,
    'VND': 5,
    'MYR': 22,
    'TWD': 10,
    'MAD': 41,
    'MXN': 42,
    'RUB': 11,
    'AUD': 7,
    'SGD': 3,
    'GBR': 12,
    'EUR': 14,
    'DZD': 117,
    'PHP': 17,
    'INR': 4,
    'CHF': 9,
    'NGN': 15,
    'IDR': 16,
    'KHR': 18,
    'BRL': 19,
    'SAR': 20,
    'AED': 21,
    'TRY': 23,
    'NZD': 24,
    'ZAR': 26,
    'NOK': 27,
    'DKK': 28,
    'SEK': 29,
    'ARS': 30,
    'THB': 31,
    'COP': 32,
    'VES': 33,
    'ALL': 46,
    'KES': 34,
    'PEN': 35,
    'CZK': 37,
    'HUF': 38,
    'ILS': 39,
    'PLN': 43,
    'RON': 44,
    'UAH': 45,
    'CLP': 53,
    'DOP': 55,
    'GEL': 56,
    'KZT': 57,
    'QAR': 59,
    'UYU': 60, 
    'UZS': 61,
    'PKR': 62,
    'BBD': 66,
    'BDT': 67,
    'BOB': 70,
    'BYN': 72,
    'EGP': 74,
    'GHS': 75,
    'HNL': 77,
    'JMD': 79,
    'KGS': 80,
    'LKR': 83,
    'MNT': 84,
    'MOP': 85,
    'MUR': 86,
    'PAB': 88,
    'PYG': 90,
    'TZS': 94,
    'UGX': 95,
    'XAF': 96,
    'XOF': 97,
    'ZMW': 98
}
CURRENCIES.update({v:k for k,v in CURRENCIES.items()})

class HuobiP2P(BaseP2P):
    
    __slots__ = ('_api', '_type', 'currency', 'cryptocurrency')
    
    def __init__(self) -> None:
        super().__init__()
        self._api = 'https://otc-api.trygofast.com/v1/data/trade-market'
        self._type = None
        
        
    async def get_orders(
        self: 'HuobiP2P', 
        currency: str, 
        cryptocurrency: str, 
        trade_type: str = 'buy') -> list[dict]:
        
        _type = trade_type.lower()
        currency = currency.upper()
        cryptocurrency = cryptocurrency.upper()

        params = {
            'coinId': CRYPTA[cryptocurrency],
            'currency': CURRENCIES[currency],
            'tradeType': _type,
            'currPage': 1,
            'payMethod': 0,
            'acceptOrder': 0,
            'country': '',
            'blockType': 'general',
            'online': 1,
            'range': 0,
            'amount': '',
            'onlyTradable': 'false',
            'isFollowed': 'false'   
        }
        response = await self._session.get(self._api, json_data=True, params=params)
        if (data := response.content):
            return data.get('data')
    
    
    async def get_order_data(self: 'HuobiP2P', order: dict) -> Order:
        
        coinid = order["coinId"]
        currency = order["currency"]
        owner = order['userName']
        owner_link = f"https://www.huobi.com/ru-ru/fiat-crypto/trader/{order['uid']}"
        paymethods = [bank['name'] for bank in order['payMethods']]
        paymethod_ids = [bank['payMethodId'] for bank in order['payMethods']]
        limit = {
            'min': float(order['minTradeLimit']),
            'max': float(order['maxTradeLimit'])
        }
        price = float(order['price'])
        exchange = 'https://www.huobi.com'
        _type = 'buy' if order["tradeType"]-1 else 'sell'

        match _type:
            case 'sell':
                rate = f"{price}:1"
                return Order(
                    market_name=self.__class__.__name__,
                    currency=CURRENCIES[currency],
                    cryptocurrency=CRYPTA[coinid],
                    exchange=exchange,
                    owner_link=owner_link,
                    owner=owner,
                    paymethod=paymethods,
                    limit=limit,
                    rate=rate,
                    paymethod_id=paymethod_ids,
                    price=price
                )
            case 'buy':
                rate = f"1:{price}"
                return Order(
                    market_name=self.__class__.__name__,
                    currency=CURRENCIES[currency],
                    cryptocurrency=CRYPTA[coinid],
                    exchange=exchange,
                    owner_link=owner_link,
                    owner=owner,
                    paymethod=paymethods,
                    limit=limit,
                    rate=rate,
                    paymethod_id=paymethod_ids,
                    price=price
                )
                
class Huobi(BaseP2P):
    __slots__ = ('_api', 'currency', 'cryptocurrency')
    
    def __init__(self) -> None:
        super().__init__()
        self._api = 'https://api.huobi.pro/market/tickers'
        
        
    async def get_orders(
        self: 'Huobi', 
        currency: str, 
        cryptocurrency: str, 
        trade_type: str = 'BUY'
        ) -> list[dict] | None:

        crypts = ('USDT','ETH', 'BTC', 'BUSD', 'BNB')
        self._session.headers['Content-Type'] = 'application/json'
        response = await self._session.get(self._api, json_data=True)
        if (data := response.content):
            res = []
            for i in crypts:
                for i2 in crypts:
                    res.append(i+i2)
            data = [i for i in data["data"] if i["symbol"].upper() in res]
            return data
      
    
    async def get_order_data(self, order: dict) -> Order:
        
        if not isinstance(order, dict):
            raise TypeError(f'order must be a dictionary, not {type(order).__name__}')
        
        crypts = ('USDT','ETH', 'BTC', 'BUSD', 'BNB')
        for i in range(len(order['symbol'])):
            if order['symbol'][:i].upper() in crypts:
                crypt1 = order['symbol'][:i].upper()
                crypt2 = order['symbol'][i:].upper()
        
        return Order(
            market_name=self.__class__.__name__,
            currency=crypt1,
            cryptocurrency=crypt2,
            exchange="",
            owner_link=f"https://www.huobi.com/ru-ru/exchange/{crypt1.lower()}_{crypt2.lower()}/",
            owner=None,
            rate=f"1:{order['close']}",
            price=float(order['close']),
            limit=None,
            paymethod=[],
            paymethod_id=[]
        )