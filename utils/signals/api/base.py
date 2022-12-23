import abc
from pathlib import Path

from ..utils.data import Order

from ..async_requester import AsyncRequest

ROOT_DIR = Path(__file__).resolve().parent.parent

single_cookie_path = ROOT_DIR / 'api' / 'utils' / 'source' / 'cookie.json'
all_cookies_path = ROOT_DIR / 'api' / 'utils' / 'source' / 'cookies.json'

class BaseP2P(metaclass=abc.ABCMeta):
    
    __slots__ = ('_session',)
    
    def __init__(self) -> None:
        """
        Creating an aiohttp ClientSession
        """
        self._session = AsyncRequest(step=50)
        
    @abc.abstractmethod
    async def get_orders(self, currency: str = ..., cryptocurrency: str = ..., trade_type: str = ...) -> list[dict]: 
        """basic function that getting orders from exchange site

        Args:
            currency (str): a fiat currency. Like 'RUB' or any 
            cryptocurrency (str): cryptocurrency. Like 'BTC' or any. BTC only for https://totalcoin.io
            trade_type (str, optional): Basic BUY or SELL type

        Returns:
            list[dict]: list with data as dictionary.
        """
    
    @abc.abstractmethod
    async def get_order_data(order: dict = ...) -> Order: 
        """basic function that collecting order data

        Args:
            order (dict): taken a dictionary

        Returns:
            Order: an Order object with data
        """
    