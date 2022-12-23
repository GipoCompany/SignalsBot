from datetime import datetime
import json
import asyncpg

from utils.config import db
from utils import types
from utils.signals.utils.data import Order

async def connect() -> asyncpg.Connection:
    conn = await asyncpg.connect(
        host = db.host,
        port = db.port,
        user = db.user.name,
        password = db.user.password,
        database = db.database
    )
    return conn

async def check(msg = None, user_id = None) -> types.Users:
    conn = await connect()
    res = await conn.fetchrow(f"INSERT INTO users (user_id) SELECT {msg.from_user.id if msg else user_id} WHERE NOT EXISTS (SELECT user_id FROM users WHERE user_id = {msg.from_user.id if msg else user_id}) RETURNING *;")
    await conn.close()
    res = types.Users(res) if res else await get.users(user_id=msg.from_user.id if msg else user_id)
    return res

class get:
    async def settings(index=-1) -> types.Settings:
        conn = await connect()
        res = await conn.fetch("SELECT * FROM settings ORDER BY settings_v DESC;")
        await conn.close()
        return types.Settings(res[index])

    async def users(**kwargs) -> list[types.Users] | types.Users:
        conn = await connect()
        if kwargs:
            where = ' AND '.join([f"{k} = {v}" for k,v in kwargs.items()]) 
            res = await conn.fetch(f"SELECT * FROM users WHERE {where};")
        else:
            res = await conn.fetch(f"SELECT * FROM users;")
        await conn.close()
        return None if not res else [types.Users(user) for user in res] if len(res) > 1 else types.Users(res[0])

    async def signals(user_id: int | None = None):
        conn = await connect()
        if not user_id:
            res = await conn.fetch("SELECT * FROM signals;")
            await conn.close()
            return list(filter(lambda x: x.spread > 0, [types.Signal(signal) for signal in res]))
        res = await conn.fetch(f"SELECT * FROM signals WHERE user_id={user_id}")
        return sorted(filter(lambda x: (datetime.now() - x.date).total_seconds() < 60*5, [types.Signal(signal) for signal in res]), key=lambda x: x.spread, reverse=True)

class add:
    async def signals(signals: list[list[Order]] | None, user: types.Users):# -> list[types.Signal]:
        if not signals:
            return None

        conn = await connect()
        signals = sorted(signals, key=lambda signal: (user.balance / signal[0].price * signal[1].price * signal[2].price) / (user.balance / 100) - 100, reverse=True)[:20]
        signals_spread = [round((user.balance / signal[0].price * signal[1].price * signal[2].price) / (user.balance / 100) - 100, 2) for signal in signals]
        signals_to_db = [", ".join([str(user.user_id), str(signals_spread[i]*100), f"'{json.dumps({k+1:v.to_dict() for k, v in enumerate(signals[i])})}'"]) for i in range(len(signals))]
        lines = "(" + "), (".join(signals_to_db) + ")"

        res = await conn.fetch(f"INSERT INTO signals (user_id, spread, steps) VALUES {lines} RETURNING *;")
        await conn.close()
        return sorted([types.Signal(signal) for signal in res], key=lambda x: x.spread, reverse=True)

class edit:
    async def users(user_id=None, arg=None, **kwargs) -> list[types.Users] | types.Users:
        conn = await connect()
        set = arg if arg else ', '.join([f"{k}={v}" for k,v in kwargs.items()])
        res = await conn.fetchrow(f"UPDATE users SET {set} WHERE user_id={user_id} RETURNING *;") if user_id else await conn.fetch(f"UPDATE users SET {', '.join([f'{k}={v}' for k,v in kwargs.items()])} {'WHERE' if arg else ''} {arg if arg else ''} RETURNING *;")
        await conn.close()
        return types.Users(res) if not isinstance(res, list) else [types.Users(user) for user in res]

class delete:
    ...
