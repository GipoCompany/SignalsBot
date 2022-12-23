from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json

from utils.signals.utils.data import Order

class TypesBase:
    def __init__(self, data):
        self._data = data

    def items(self):
        return self._data.items()

    def __str__(self):
        return self.__class__.__name__ + "(" + ''.join([f"{k}=" + (f"\"{v}\"" if isinstance(v, str) else str(v)) + ", " for k, v in self._data.items()]).strip(", ") + ")"
    def __repr__(self):
        return self.__str__()

class Settings(TypesBase):
    def __init__(self, data):
        self.settings_v: int = data["settings_v"]
        self.settings_t: datetime = data["settings_t"]
        self.start_msg: str = data["start_msg"]
        self.using_msg: str = data["using_msg"]
        self.getsign_msg: str = data["getsign_msg"]
        self.suborsign_msg: str = data["suborsign_msg"]
        self.setpaymethod_msg: str = data["setpaymethod_msg"]
        self.buysub_msg: str = data["buysub_msg"]
        self.buysub_price: int = data["buysub_price"]
        self.first_buysub_price: int = data["first_buysub_price"]
        self.buysign_msg: str = data["buysign_msg"]
        self.buysign_price: int = data["buysign_price"]
        self.walletTRC20: str = data["wallet_trc20"]
        self.walletBEP20: str = data["wallet_bep20"]

        self._data = data

class Users(TypesBase):
    def __init__(self, data):
        data = {k:v for k,v in data.items()}

        self.user_id: int = data["user_id"]
        self.access_lvl: int = data["access_lvl"]
        self.subscribe: datetime = data["subscribe"]
        self.subscribe_count: int = data["subscribe_count"]
        self.reserve_signal: int = data["reserve_signal"]
        self.signal: int = data["signal"] + data["signal_free"]
        self.signal_count: int = data["signal_count"]
        self.signal_free: int = data["signal_free"]
        self.paymethods = data["paymethods"] = data["paymethods"].split("_#_")
        self.balance: float = float(data["balance"])
        self.wallet: str = data["wallet"]
        self.lasthash: str = data["lasthash"]

        self._data = data

class Signal(TypesBase):
    def __init__(self, data):
        data = {k:v for k,v in data.items()}

        self.id: int = data["id"]
        self.user_id: int = data["user_id"]
        self.date: datetime = data["date"]
        self.spread: float = data["spread"] / 100
        self.steps: list[Order] = [Order(**v) for k,v in json.loads(data["steps"]).items()]

        data["steps"] = self.steps
        self._data = data

class transTRC20(TypesBase):
    def __init__(self, data):
        self.hash: str = data["transaction_id"]
        self.from_: str = data["from_address"]
        self.to_: str = data["to_address"]
        self.amount: float = int(data["quant"]) / int("1"+("0"*data["tokenInfo"]["tokenDecimal"]))
        self.token: str = data["tokenInfo"]["tokenAbbr"]

        self._data = {"hash": self.hash, "from_": self.from_, "to_": self.to_, "amount": self.amount, "token": self.token}

class transBEP20(TypesBase):
    def __init__(self, data: BeautifulSoup, to_):
        data = data.find_all('td')

        self.hash: str = data["hash"]
        self.from_: str = data["to"]
        self.to_: str = data["from"]
        self.amount: float = int(data["value"]) / int("1"+("0"*data["tokenDecimal"]))

        self._data = {"hash": self.hash, "from_": self.from_, "to_": self.to_, "amount": self.amount, "token": self.token, "time": self.time}

class Transaction(TypesBase):
    TRC20 = transTRC20
    BEP20 = transBEP20
        