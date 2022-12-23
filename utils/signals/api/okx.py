from datetime import datetime
import logging

from ..utils.data import Order
from .base import BaseP2P



class OkxP2P(BaseP2P):
    
    __slots__ = ('_api', 'currency', 'cryptocurrency')
    
    def __init__(self) -> None:
        super().__init__()
        self._api = 'https://www.okx.com'
        
    
    async def get_orders(
        self: 'OkxP2P', 
        currency: str, 
        cryptocurrency: str, 
        trade_type: str = 'buy'
        ) -> dict[list]:
        trade_type = trade_type.lower()
        timestamp = datetime.now().timestamp()
        _api = f'{self._api}/v3/c2c/tradingOrders/books'
        currency = currency.upper()
        cryptocurrency = cryptocurrency.upper()
        params = {
            't': timestamp,
            'quoteCurrency': currency,
            'baseCurrency': cryptocurrency,
            'side': trade_type,
            'paymentMethod': 'all',
            'userType': 'all', 
            'showTrade': 'false',
            'showFollow': 'false',
            'showAlreadyTraded': 'false',
            'isAbleFilter': 'false'
        }
        response = await self._session.get(_api, json_data=True, params=params)
 
        if (data := response.content):
            return data.get('data')[trade_type]   
    
   
    async def get_order_data(self, order: dict) -> Order:
        
        trade_type = order['side']
        owner = order['nickName']
        owner_link = f"{self._api}/ru/p2p/ads-merchant?publicUserId={order['publicUserId']}"
        price = float(order['price'])
        limit = {
            'min': float(order['quoteMinAmountPerOrder']),
            'max': float(order['quoteMaxAmountPerOrder'])
        }
        paymethods = order['paymentMethods']
        paymethods_ids = [index for index in range(len(paymethods))]
        match trade_type:
            case 'buy':
                rate = f"1:{price}"
                return Order(
                    market_name=self.__class__.__name__,
                    currency=order["quoteCurrency"].upper(),
                    cryptocurrency=order["baseCurrency"].upper(),
                    exchange=self._api,
                    owner_link=owner_link,
                    owner=owner,
                    price=price,
                    rate=rate,
                    limit=limit,
                    paymethod=paymethods,
                    paymethod_id=paymethods_ids
                )
            case 'sell':
                rate = f"{price}:1"
                return Order(
                    market_name=self.__class__.__name__,
                    currency=order["quoteCurrency"].upper(),
                    cryptocurrency=order["baseCurrency"].upper(),
                    exchange=self._api,
                    owner_link=owner_link,
                    owner=owner,
                    price=price,
                    rate=rate,
                    limit=limit,
                    paymethod=paymethods,
                    paymethod_id=paymethods_ids
                )

class Okx(BaseP2P):
    def __init__(self) -> None:
        super().__init__()
        self._api = 'https://www.okx.com/api/v5/market/index-tickers'
        
        
    async def get_orders(
        self: 'Okx', 
        currency: str, 
        cryptocurrency: str, 
        trade_type: str = 'BUY'
        ) -> list[dict] | None:

        self._session.headers['Content-Type'] = 'application/json'
        res = []
        for i in ('ETH-USDT', 'BTC-USDT'):
            response = await self._session.get(self._api + f'?instId={i}', json_data=True)
            if (data := response.content):
                if data.get('data'):
                    res.append(data.get('data')[0])
                else:
                    logging.warning(f"Okx return {response.status_code} code;  cc: {cryptocurrency}; c: {currency}; td: {trade_type}")
            else:
                logging.warning(f"Okx return {response.status_code} code;  cc: {cryptocurrency}; c: {currency}; td: {trade_type}")
        return res
    
    async def get_order_data(self, order: dict) -> Order:
        
        if not isinstance(order, dict):
            raise TypeError(f'order must be a dictionary, not {type(order).__name__}')
        
        crypt1, crypt2 = order['instId'].split("-")
        
        return Order(
            market_name=self.__class__.__name__,
            currency=crypt1,
            cryptocurrency=crypt2,
            exchange="",
            owner_link=f"https://www.okx.com/ru/trade-spot/{crypt1}-{crypt2}",
            owner=None,
            rate=f"1:{order['idxPx']}",
            price=float(order['idxPx']),
            limit=None,
            paymethod=[],
            paymethod_id=[]
        )
            