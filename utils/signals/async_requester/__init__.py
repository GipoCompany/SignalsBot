from aiohttp import ClientSession

import asyncio
from typing import AsyncGenerator, Any, NoReturn
import sys

from .decorators import connection_retry
from .metaclasses import Singleton
from .utils import Response, get_random_useragent


__all__ = [
    'get_random_useragent',
    'AsyncRequest',
    'get_latest_useragent'
]



class AsyncRequest(metaclass=Singleton):
    """
    A Singleton class that makes async request and getting data from url/urls
    <options> contents simple request options:
        auth,
        json,
        data,
        params,
        allow_redirects,
        cookies,
        headers,
        ...
    step variable indicates how many requests in a row do you want to do.
    NOTE:
        - Do not try to use 1000/2000/etc step value (but it may work)
        remember, we should be nice to the server
        Usage:
            AsyncRequest().get('https://google.com') -> to get single site data
            AsyncRequest().post('https://google.com') -> post request
            ...
            AsyncRequest().collect_data(['https://google.com', 'https://youtube.com']) -> to get a list with sites data
    """
    def __init__(self, step: int = 10, as_session: bool = True) -> None:
        
        if not isinstance(as_session, bool):
            raise TypeError(f'as_session should be bool type, not {type(as_session).__name__}')
        
        self.step = step 
        self.headers: dict = {'user-agent': get_random_useragent()}
        self.__session: ClientSession = self.create_session(session=as_session) 
        
        
    async def create_session(self, session: bool) -> ClientSession:
        '''Making session'''
        if not session:
            while True:
                async with ClientSession(headers=self.headers) as session:
                    yield session
        else:
            async with ClientSession(headers=self.headers) as session:
                while True:
                    yield session
         
         
    async def send_session_close(self) -> None:
        session = await anext(self.__session)
        return await session.close()
                
                
    async def get(self, url: str, json_data: bool = False, **options) -> Response | NoReturn:
        return await self._fetch(url=url, method='get', json_data=json_data, **options)
    
    
    async def post(self, url: str, json_data: bool = False, **options) -> Response | NoReturn:
        return await self._fetch(url=url, method='post', json_data=json_data, **options)
    
    
    async def patch(self, url: str, json_data: bool = False, **options) -> Response | NoReturn:
        return await self._fetch(url=url, method='patch', json_data=json_data, **options)
    
    
    async def options(self, url: str, json_data: bool = False, **options) -> Response | NoReturn:
        return await self._fetch(url=url, method='options', json_data=json_data, **options)
    
    
    async def put(self, url: str, json_data: bool = False, **options) -> Response | NoReturn:
        return await self._fetch(url=url, method='put', json_data=json_data, **options)
    
    
    async def delete(self, url: str, json_data: bool = False, **options) -> Response | NoReturn:
        return await self._fetch(url=url, method='delete', json_data=json_data, **options)
    

    async def head(self, url: str, json_data: bool = False, **options) -> Response | NoReturn:
        return await self._fetch(url=url, method='head', json_data=json_data, **options)

    @connection_retry
    async def _fetch(
        self, 
        url: str, 
        method: str, 
        json_data: bool = False, 
        **options
        ) -> Response | NoReturn:
        """
        Args:
            url (str): a url that data you want get from
            method (str, optional): request method. 
            json_data (bool, optional): equal to .json() from basic request. Defaults to False.

        Raises:
            AttributeError: Supports only get/post/put/patch/options methods

        Returns:
            Response: a data from request
        """
        session = await anext(self.__session) # getting current session
        request = {
            'post': session.post,
            'get': session.get,
            'put': session.put,
            'options': session.options,
            'patch': session.patch,
            'delete': session.delete,
            'head': session.head
        }
        
        if method not in request:
            raise AttributeError(f'Expected request method, got {method}')
        if not options.get('headers'):
            options['headers'] = self.headers
     
    
        async with request[method](url=url, **options) as response:
            if response.status == 200:
                return Response(
                    content=await response.read() if not json_data else await response.json(),
                    request_url=url,
                    response_url=response.url,
                    headers=response.headers,
                    cookies=response.cookies,
                    status_code=response.status
                )
            return Response(
                    request_url=url,
                    response_url=response.url,
                    headers=response.headers,
                    cookies=response.cookies,
                    status_code=response.status
                )
    
    async def _collect_tasks(
        self, 
        urls: list | tuple, 
        method: str, 
        json_data: bool = False, 
        **options
        ) -> AsyncGenerator[list[Response], Any]:
        """

        Args:
            urls (list | tuple): a urls that data you want to get from
            method (str, optional): same to ._fetch() method
            json_data (bool, optional): same to ._fetch() method

        Yields:
            Iterator[list[Response]]: returns an AsyncGenerator with list of responses inside
        """
        if not isinstance(urls, (tuple, list)):
            urls = tuple(urls)
        step = self.step if len(urls) >= self.step else len(urls)
        tasks = set()
        for index in range(0, len(urls), step):
            for url in urls[index:index+step]:
                tasks.add(asyncio.create_task(self._fetch(url, method=method, json_data=json_data, **options)))
            yield await asyncio.gather(*tasks)
            tasks.clear()
            
    async def collect_data(
        self, 
        urls: list | tuple, 
        method: str = 'get', 
        json_data: bool = False, 
        **options
        ) -> AsyncGenerator[list[Response], Any]:
        return self._collect_tasks(urls, method=method, json_data=json_data, **options)



async def get_latest_useragent() -> str | None:
    """
    Returns:
        str | None: Trying to get the latest useragent for your browser
        
    It's can be useful if site has cloudflare and checks your platform with useragent
    and compare it. But it may be not enough, check on cookies as well.
    """
    return 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    #linux_ua = 'Mozilla/5.0 (X11; Linux x86_64)'
    #windows_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    #session = AsyncRequest()
    #response = await session.get('https://www.whatismybrowser.com/guides/the-latest-user-agent/windows')
    #data = await response.html.select('table > tbody > tr')
    #new_ua = None
 #
    #for col in data:
    #    chrome = col.select_one('td > b')
    #    if chrome and chrome.get_text(strip=True).lower() == 'chrome':
    #        ua = col.select_one('span.code')
    #        if ua:
    #            new_ua = ua.get_text(strip=True)
    #            break
    #if new_ua:
    #    new_data = new_ua.split(')', 1)[-1]
    #    
    #    match sys.platform:
    #        case 'win32':
    #            new_ua = f'{windows_ua}{new_data}'
    #        case 'linux' | 'linux2':
    #            new_ua = f'{linux_ua}{new_data}'
    #        case _:
    #            raise Exception(f'This function expected Linux or Windows platform, not {sys.platform}')
    #    
    #return new_ua
    