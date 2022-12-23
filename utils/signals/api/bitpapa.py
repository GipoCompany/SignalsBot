import json
from .base import BaseP2P
from ..utils.data import Order
import requests

DEF_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'

class BitpapaP2P(BaseP2P):
    
    #__slots__ = (
    #    '_api', 
    #    'token', 
    #    'user_agent', 
    #    'cookie_data', 
    #    'currency', 
    #    'cryptocurrency'
    #    )
    
    def __init__(self) -> None:
        super().__init__()
        self._api = 'https://bitpapa.com'
        self.ss = requests.Session()
        self.ss.headers.update({'User-Agent': DEF_UA})
        #self.cookie_data = set_cookie(self._api, all_cookies_path)
        #self.token = self.cookie_data.get(self._api, {}).get('cookies')
        #self.user_agent = self.cookie_data.get(self._api, {}).get('user-agent')
    
    
    async def get_orders(
        self: 'BitpapaP2P', 
        currency: str, 
        cryptocurrency: str, 
        trade_type: str = 'buy') -> list[dict]:
        
        trade_type = trade_type.lower()
        currency = currency.upper()
        cryptocurrency = cryptocurrency.upper()
        api = f'{self._api}/api/v1/pro/search'
        params = {
            'crypto_amount': '',
            'type': trade_type,
            'page': 1,
            'sort': 'price',
            'currency_code': currency,
            'previous_currency_code': currency,
            'crypto_currency_code': cryptocurrency,
            'with_correct_limits': 'false',
            'limit': 20
        }
        response = self.ss.get(api, params=params)
        
        result_obj = json.loads(response.text)
        
        return result_obj['ads'] if result_obj.get('ads') else None
          

    async def get_order_data(self: 'BitpapaP2P', order: dict) -> Order:
        
        trade_type = order['type']
        
        owner = order['user']['user_name']
        owner_link = f'{self._api}/user/{owner}'
        limit = {
            'min': float(order['limit_min']),
            'max': float(order['limit_max'])
        }
        paymethod = [bank['name'] for bank in order['payment_method_banks']]
        paymethod_ids = [bank['id'] for bank in order['payment_method_banks']]
        price = float(order['price'])
        
        match trade_type:
            case "Ad::Sell":
                rate = f"{order['price']}:1"
                return Order(
                    market_name=self.__class__.__name__,
                    currency=order["currency_code"],
                    cryptocurrency=order["crypto_currency_code"],
                    exchange=self._api,
                    owner_link=owner_link,
                    owner=owner,
                    price=price,
                    limit=limit,
                    rate=rate,
                    paymethod=paymethod,
                    paymethod_id=paymethod_ids
                    
                )
            case "Ad::Buy":
                rate = f"1:{order['price']}"
                return Order(
                    market_name=self.__class__.__name__,
                    currency=order["currency_code"],
                    cryptocurrency=order["crypto_currency_code"],
                    exchange=self._api,
                    owner_link=owner_link,
                    owner=owner,
                    price=price,
                    limit=limit,
                    rate=rate,
                    paymethod=paymethod,
                    paymethod_id=paymethod_ids
                    
                )
