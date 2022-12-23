from crypt import crypt
from dataclasses import dataclass
import json

from ..utils.data import Order



@dataclass(frozen=True, slots=True)
class Crypt:
    BTC: list[Order]
    USDT: list[Order]
    ETH: list[Order]
    BUSD: list[Order]
    BNB: list[Order]
    DOGE: list[Order]

@dataclass(frozen=True, slots=True)
class Exchange:
    buy_orders: list[Order] | None = None
    sell_orders: list[Order] | None = None

    if all([buy_orders, sell_orders]):
        raise AttributeError('Only one parameter should be not empty, not both')

    def sort_crypts(self) -> Crypt:
        cryptocurrencies = {
            'BTC': [],
            'USDT': [],
            'ETH': [],
            'BUSD': [],
            'BNB': [],
            'DOGE': [],
        }
        if self.buy_orders:
            orders = self.buy_orders
        else:
            orders = self.sell_orders

        for order in orders:
            crypt = order.cryptocurrency
            cryptocurrencies[crypt.upper()].append(order)

        return Crypt(**cryptocurrencies)
                

@dataclass(frozen=True, slots=True)
class OrderSet:
    _buy: list[Order] 
    _sell: list[Order] 
    _ctc: list[Order]

    @property
    def buy(self) -> Exchange:
        return Exchange(self._buy, None)

    @property
    def sell(self) -> Exchange:
        return Exchange(None, self._sell)

    @property
    def ctc(self) -> Exchange:
        return Exchange(self._ctc, None)

    def get_buy(self, paymethods: list[str], balance: float, laststep: list | None) -> list[list[Order]] | None:
        if laststep == None:
            return None
        crypts = self.buy.sort_crypts()
        newstep = laststep[:]
        for orders in [crypts.BTC, crypts.USDT, crypts.ETH, crypts.BUSD, crypts.BNB, crypts.DOGE]:
            for order in orders:
                if order == None or not [bank for bank in order.paymethod if bank and bank.lower() in [paym.lower() for paym in paymethods]] or order.limit.get("min") > balance or order.limit.get("max") < balance:
                    continue
                elif not laststep:
                    newstep.append([order])
        return newstep


    def get_sell(self, paymethods: list[str], balance: float, laststep: list | None) -> list[list[Order]] | None:
        if not laststep:
            return None
        crypts = self.sell.sort_crypts()
        newstep = laststep[:]
        for orders in [crypts.BTC, crypts.USDT, crypts.ETH, crypts.BUSD, crypts.BNB, crypts.DOGE]:
            for order in orders:
                if order == None or not [bank for bank in order.paymethod if bank.lower() in [paym.lower() for paym in paymethods]] or order.limit.get("min") > balance or order.limit.get("max") < balance:
                    continue
                for i in range(len(laststep)):
                    if not laststep[i]:
                        del laststep[i]
                    elif order.cryptocurrency != laststep[i][-1].cryptocurrency:
                        continue
                    elif len(laststep[i]) == 2:
                        newstep[i].append(order)
                    else:
                        newstep.append(laststep[i][:-1])
                        newstep[-1].append(order)
        return newstep

    def get_ctc(self, laststep: list[list[Order]] | None) -> list[list[Order]] | None:
        if not laststep:
            return None
        crypts = self.ctc.sort_crypts()
        newstep = laststep[:]
        for orders in [crypts.BTC, crypts.USDT, crypts.ETH, crypts.BUSD, crypts.BNB, crypts.DOGE]:
            for order in orders:
                if order == None:
                    continue
                for i in range(len(laststep)):
                    if not laststep[i]:
                        del laststep[i]
                    elif order.currency != laststep[i][0].cryptocurrency:
                        continue
                    elif len(laststep[i]) == 1:
                        newstep[i].append(order)
                    else:
                        newstep.append(laststep[i][:-1])
                        newstep[-1].append(order)
        return newstep

    def get_signals(self, paymethods: list[str], balance: float) -> list[list[Order]] | None:
        paymethods = [i.split(":")[0] for i in paymethods if int(i.split(":")[1])]
        step1 = self.get_buy(paymethods, balance, [])
        step2 = self.get_ctc(step1)
        step3 = self.get_sell(paymethods, balance, step2)
        f = lambda sign: (balance / sign[0].price * sign[1].price * sign[2].price)
        return sorted([sign for sign in step3 if len(sign) == 3 and f(sign) > balance], key=f, reverse=True) if step3 else None
