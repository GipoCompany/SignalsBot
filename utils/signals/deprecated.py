import asyncio

from api import get_orders_data
from api.binance import BinanceP2P
from api.bitzlato import BitzlatoP2P
from api.bitpapa import BitpapaP2P
from api.huabi import HuabiP2P
from api.okx import OkxP2P
from api.totalcoin import TotalcoinP2P

     
     
# CRYPTOCURR = ['USDT', 'ETH', 'BTC', 'TRX', 'BUSD', 'BNB', 'DOGE'] # needable
async def totalcoin_test():
    # BTC only
    for trade_type in ('BUY', 'SELL'):
        btc_only_gen = get_orders_data(TotalcoinP2P(), trade_type=trade_type, cryptocurrency='BTC')
        async for order in btc_only_gen:
            if order:
                print(f'{trade_type} {order.rate} {order.find_paymethod("tinkoff")}')
                
            
async def okx_test():
    CRYPTOCURR = ['USDT', 'ETH', 'BTC'] # allowed currencies of needable
    for trade_type in ('BUY', 'SELL'):
        for crypt in CRYPTOCURR:
            orders_gen = get_orders_data(OkxP2P(), cryptocurrency=crypt, trade_type=trade_type)
            async for order in orders_gen:
                if order:
                    print(f'{crypt} {trade_type} {order.rate} {order.find_paymethod("tinkoff")}')
                
async def huabi_test():
    CRYPTOCURR = ['USDT', 'ETH', 'BTC'] # allowed currencies of needable
    for trade_type in ('BUY', 'SELL'):
        for crypt in CRYPTOCURR:
            orders_gen = get_orders_data(HuabiP2P(), cryptocurrency=crypt, trade_type=trade_type)
            async for order in orders_gen:
                if order:
                    print(f'{crypt} {trade_type} {order.rate} {order.owner} {order.find_paymethod("tinkoff")}')
                
async def bitzlato_test():
    bp = BitzlatoP2P(domen='.com') # it need to initialize first
    CRYPTOCURR = ['USDT', 'ETH', 'BTC', 'DOGE'] # allowed currencies of needable
    for trade_type in ('BUY', 'SELL'):
        for crypt in CRYPTOCURR:
            # you can set your domen instead .net/.bz/.com
            orders_gen = get_orders_data(bp, cryptocurrency=crypt, trade_type=trade_type)
            async for order in orders_gen:
                if order:
                    print(f'{crypt} {trade_type} {order.rate} {order.owner} {order.find_paymethod("tinkoff")}')

async def bitpapa_test():
    bp = BitpapaP2P() # it need to initialize first
    CRYPTOCURR = ['USDT', 'ETH', 'BTC'] # allowed currencies of needable
    for trade_type in ('BUY', 'SELL'):
        for crypt in CRYPTOCURR:
            orders_gen = get_orders_data(bp, cryptocurrency=crypt, trade_type=trade_type)
            async for order in orders_gen:
                if order:
                    print(f'{crypt} {trade_type} {order.rate} {order.owner} {order.find_paymethod("tinkoff")}')

async def binance_test():
    CRYPTOCURR = ['USDT', 'ETH', 'BTC', 'BUSD', 'BNB'] # allowed currencies of needable
    for trade_type in ('BUY', 'SELL'):
        for crypt in CRYPTOCURR:
            orders_gen = get_orders_data(BinanceP2P(), cryptocurrency=crypt, trade_type=trade_type)
            async for order in orders_gen:
                if order:
                    print(f'{crypt} {trade_type} {order.rate} {order.owner} {order.find_paymethod("tinkoff")}')
              
                
async def main():
    await totalcoin_test()
    await okx_test()
    await huabi_test()
    #await bitzlato_test()
    #await bitpapa_test()
    await binance_test()
    
  
   
        
if __name__ == '__main__':
    asyncio.run(main())
