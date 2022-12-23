import asyncio
import sys, warnings
from typing import Any, Awaitable, Callable, TypeVar, cast
from functools import wraps, partial

from .utils import info



if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


T = TypeVar("T", bound=Callable[..., Any])


def decohints(decorator: Callable) -> Callable:
    return decorator


def connection_retry(func):
    '''A simple decorator 
    handle errors that may appear due to the abundance of requests or incorrect data
    If error appear -> tries to retry request 5 times with 2 seconds delay
    '''
    @wraps(func)
    async def wrap(*args, **kwargs):
        retries = 1
        while retries < 6:
            try:
                result = await func(*args, **kwargs)
            except Exception as ex:
                info(f'Got unexpected error {ex}\n'
                    f'Retrying to connect...{retries}')
                retries += 1
                await asyncio.sleep(2)
            else:
                return result
        raise Exception('Maximum connections retries exceeded')
    return wrap


def async_test(coro):
    """
    Simple decorator to run async tests with unittest. Ignoring ResourceWarning
    """
    @wraps(coro)
    def wrapper(*args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
        
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(coro(*args, **kwargs))
            finally:
                loop.close()
    return wrapper

@decohints
def sync_to_async(func: T) -> Awaitable[T]:
    @wraps(func)
    async def run_in_executor(*args, **kwargs):
        loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, pfunc)

    return cast(Awaitable[T], run_in_executor)
    