from .base import BaseP2P
from ..utils.data import Order
from ..async_requester import get_latest_useragent, get_random_useragent



class TotalcoinP2P(BaseP2P):
    
    __slots__ = ('_api', 'currency', 'cryptocurrency')
    
    def __init__(self: 'TotalcoinP2P') -> None:
        super().__init__()
        self._api = 'https://totalcoin.io'
        
        
    async def get_orders(
        self: 'TotalcoinP2P', 
        currency: str, 
        trade_type: str,
        cryptocurrency = 'BTC' # buffer parameter
        ) -> list[dict] | None:
        _api = f'{self._api}/ru/offers/ajax-offers-list'

        self.cryptocurrency = cryptocurrency
        self.currency = currency.lower()
        params = {
            'type': trade_type.lower(),
            'currency': self.currency,
            'pm': '',
            'pro': '0'
        }
        self._session.headers.update({
            'content-type': 'application/json; charset=UTF-8',
            'user_agent': ua if (ua := await get_latest_useragent()) else get_random_useragent(),
            'x-requested-with': 'XMLHttpRequest'
            })
        
        response = await self._session.get(_api, json_data=True, params=params, compress=True)
        if (data := response.content):
            return data.get('data')[:20]
    

    async def get_order_data(self, order: dict) -> Order:
        
        trade_type = order['type']
        
        owner = order['user']['nickname']
        owner_link = None # there are flexiable elements...
        limit = {
            'min': float(order['limitMin']),
            'max': float(order['limitMax'])
        }
        price = float(order['price'])
        paymethod = (order['paymentMethod']['name'],)
        paymethod_id = order['paymentMethod']['paymentMethodId']
        
        match trade_type:
            case 'SELL':
                rate = f"{price}:1"
                return Order(
                    market_name=self.__class__.__name__,
                    currency=self.currency,
                    cryptocurrency=self.cryptocurrency,
                    exchange=self._api,
                    owner_link=owner_link,
                    owner=owner,
                    rate=rate,
                    price=price,
                    paymethod=paymethod,
                    limit=limit,
                    paymethod_id=paymethod_id
                )
            case 'BUY':
                rate = f"1:{price}"
                return Order(
                    market_name=self.__class__.__name__,
                    currency=self.currency,
                    cryptocurrency=self.cryptocurrency,
                    exchange=self._api,
                    owner_link=owner_link,
                    owner=owner,
                    rate=rate,
                    price=price,
                    paymethod=paymethod,
                    limit=limit,
                    paymethod_id=paymethod_id
                )
    