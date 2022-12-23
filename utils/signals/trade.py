import asyncio
import json

from algorithm import get_orders


async def main():
    orders = await get_orders()
    balance = 20000.0
    signals = orders.get_signals(paymethods=['tinkoff:1', 'sberbank:1', 'payeer:1', 'alfabank:1', 'qiwi:1', 'yoomoney:1'], balance=balance)
    spread = lambda x: f'{(balance / x[0].get("price") * x[1].get("price") / x[2].get("price") * x[3].get("price")) / (balance / 100)}%'
    tojson = {
        i: {
            'spread': spread(signals[i]),
            'signal': signals[i]
        }
        for i in range(len(signals))
    }
    with open("test.json", "w+") as file:
        json.dump(tojson, file, indent=4)

if __name__ == '__main__':
    asyncio.run(main())