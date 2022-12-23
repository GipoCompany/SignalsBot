from . import start
from . import get_signal
from . import buy
from . import owners
from . import admins
from . import no_ident

async def load(dp):
    await start.load(dp)
    await get_signal.load(dp)
    await buy.load(dp)
    # eval
    # await owners.load(dp)
    await admins.load(dp)
    await no_ident.load(dp)

__all__ = ["load"]