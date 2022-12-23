from dataclasses import dataclass 
from typing import Iterable
from difflib import SequenceMatcher as match

@dataclass(frozen=True, slots=True)
class Order:
    market_name: str
    exchange: str
    owner_link: str
    owner: str 
    price: float 
    rate: float | str
    paymethod: tuple | list | Iterable
    limit: dict
    paymethod_id: int | list | Iterable
    currency: str 
    cryptocurrency: str

    def to_dict(self) -> dict:
        """Set all object data to a dictionary
        """
        return {
            'market_name': self.market_name,
            'exchange': self.exchange,
            'owner_link': self.owner_link,
            'owner': self.owner,
            'price': self.price,
            'rate': self.rate,
            'paymethod': self.paymethod,
            'paymethod_id': self.paymethod_id,
            'limit': self.limit, 
            'currency': self.currency,
            'cryptocurrency': self.cryptocurrency

        }
    
    def find_paymethod(self, name: str | list) -> str | None:
        """finding specific paymethod

        Args:
            name (str): a string name

        Raises:
            TypeError: only if you put anything but not string in :param: name

        Returns:
            str | None: string result or None
        """

        if not isinstance(name, str | list):
            raise TypeError(f'name should be str type, not {type(name).__name__}')

        paymethods = {
            'tinkoff': 'тинькофф',
            'sberbank': 'сбербанк',
            'payeer': 'пейер',
            'alfabank': 'альфабанк',
            'qiwi': 'киви',
            'yoomoney': 'юмани',
            'юmoney': 'юмани'
        }

        if isinstance(name, list):
            return any([self.__find_paymethod(n.lower(), paymethods) == n.lower() for n in name])

        name = name.lower()

        if paymethods.get(name) is None:
            return        

        return self.__find_paymethod(name, paymethods)
        

    def __find_paymethod(self, name: str, paymethods: dict) -> str | None:
        for need in paymethods:
            for currently in self.paymethod:
                if not currently:
                    continue
                currently = currently.lower()
                if (match(a=need, b=currently).ratio() >= 0.5 or\
                    match(a=paymethods[need], b=currently).ratio()) >= 0.5 and\
                        need == name:
                    return need 
