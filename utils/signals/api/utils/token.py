
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait as Wait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException
from selenium.webdriver.chrome.webdriver import WebDriver

from ...async_requester.decorators import sync_to_async
from ...utils.logging import log

import logging, os, json, time
from pathlib import Path, PosixPath


logging.getLogger('WDM').setLevel(level=logging.WARNING)



class Cookie:
   
    __slots__ = ('_source_path')
    
    def __init__(self) -> None:
        self._source_path = Path(__file__).resolve().parent / 'source'
        os.makedirs(self._source_path, exist_ok=True)

    @staticmethod
    def _get_driver(not_visible: bool) -> WebDriver:
        """
        Args:
            not_visible (bool): A parameter that turn on headless mode. Are not working corrently

        Yields:
            _type_: Creates and Yield a WebDriver object
        """
        while True:
            yield uc.Chrome(headless=False, service=Service(ChromeDriverManager().install()), use_subprocess=True)
                
                
    def connect_and_fetch(
        self, 
        api: str, 
        not_visible: bool = False, # not working currently
        cookie_name: str | None = 'cf_clearance', # basic cloudflare token
        timeout: int = 15,
        safety: bool = False,
        minimaze: bool = False
        ) -> dict | list[dict]:
        
        
        if api.startswith('http'):
            base = api.split('/')
            name_domen = base[2]
            api = f'{base[0]}//{name_domen}'
        else:
            base = api.split('/')[0]
            api = f'https://{base}'
                 
        driver = next(self._get_driver(not_visible=not_visible)) # getting driver
        
        log(f'Getting cookies for {api}', level='critical', level_name=False)
        if safety:
            driver.options.add_experimental_option("excludeSwitches", ["enable-automation"])
            driver.options.add_experimental_option('useAutomationExtension', False)
            driver.options.add_argument('--disable-blink-features=AutomationControlled')
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                            "source": """
                                Object.defineProperty(navigator, 'webdriver', {
                                get: () => undefined
                                })
                            """
                            })
        try:
            if minimaze:
                # full minimazing can break the code
                # driver.minimaze_window()
                driver.set_window_size(500, 500)
            else:
                driver.maximize_window()
                
            driver.set_page_load_timeout(timeout) # main preference
            driver.get(api)
            if api == 'https://bitpapa.com':
                Wait(driver=driver, timeout=timeout).until(
                    lambda js: js.execute_script('return document.getElementById("root")') , 
                    f'Probably you have problems with connection or try to change timeout'
                )  
            elif api == 'https://bitzlato.com':
                Wait(driver=driver, timeout=timeout).until(
                    lambda js: js.execute_script('return document.getElementById("header")'), 
                    f'Probably you have problems with connection or try to change timeout'
                )
            else:
                js = driver
                for kw in ('header', 'footer', 'root', 'main', 'container', 'menu'):
                    try:
                        if js.execute_script(f'return document.getElementById("{kw}")') or\
                            js.execute_script(f'return document.querySelector(".{kw}"') or\
                                js.execute_script(f'return document.getElementsByTagName("{kw}"'):
                            break
                    except (NoSuchElementException, JavascriptException):
                        time.sleep(0.1)
                
            driver.execute_script("return window.stop();")         
        except TimeoutException:
            ...
        finally:
            agent = driver.execute_script("return navigator.userAgent")
            if isinstance(cookie_name, str):
                cookie = driver.get_cookie(cookie_name)
            else:
                cookies = driver.get_cookies()
            driver.close()
            driver.quit()
            
        
        
        if isinstance(cookie_name, str):
            if not cookie:
                raise ValueError(f'Expected dict with token data, got {type(cookie).__name__}')
            
            file = self._source_path / 'cookie.json'
            
            self.save_cookie_or_cookies(api, file, cookie, user_agent=agent)
            
            return {
                api: {
                    'cookie': {
                        cookie['name']: cookie['value'],
                    },
                    'user-agent': agent
                }
            }
        else:
            if not cookies:
                raise ValueError(f'Expected list with cookies data, got {len(cookies)} elements')
            
            file = self._source_path / 'cookies.json'
            
            self.save_cookie_or_cookies(api, file, cookies, user_agent=agent)
            
            return {
                    api: {
                        'cookies': {cookie['name']: cookie['value'] for cookie in cookies},
                        'user-agent': agent
                    }
                }
                     
    @staticmethod
    def save_cookie_or_cookies(
        api: str, 
        file_to_save: Path | PosixPath | str, 
        cookie_or_cookies: list[dict] | dict, 
        user_agent: str | None = None
        ) -> None:
        """basic saving method

        Args:
            api (str): an api or url that will set as key in dict
            file_to_save (Path | PosixPath | str): 'path to save cookies. If not it not exist -> creates new'
            cookie_or_cookies (list[dict] | dict): basic single cookie or a list with cookies
            user_agent (str | None, optional): You may add your own user agent if you wants.. Defaults to None.

        Raises:
            ValueError: Invokes only if misstypes
        """
        if isinstance(cookie_or_cookies, list):
            cookies = cookie_or_cookies
            data = {
                    api: {
                        'cookies': {cookie['name']: cookie['value'] for cookie in cookies}
                    }
                }
            if isinstance(user_agent, str):
                data[api]['user-agent'] = user_agent
                
        elif isinstance(cookie_or_cookies, dict):
            cookie = cookie_or_cookies
            data = {
                api: {
                    'cookie': {
                        cookie['name']: cookie['value']
                    }
                }
            }
            if isinstance(user_agent, str):
                data[api]['user-agent'] = user_agent
        else:
            raise TypeError(f'Expected list or dict, got {type(cookie_or_cookies).__name__}')
        
        if os.path.exists(file_to_save):
            with open(file_to_save, 'r', encoding='utf-8') as reader:
                exists_data = reader.read()
                new_data = json.loads(exists_data)
                new_data.update(data)
                with open(file_to_save, 'w', encoding='utf-8') as override:
                    json.dump(new_data, override, indent=4, ensure_ascii=False)
        else:
            with open(file_to_save, 'w', encoding='utf-8') as write:
                json.dump(data, write, indent=4, ensure_ascii=False)
    
    
def get_cookie_sync(
    api: str, 
    not_visible: bool = False, 
    cookie_name: str | None = 'cf_clearance', 
    timeout: int = 15, 
    safety: bool = False, 
    minimaze: bool = False,
    __obj: Cookie = Cookie(), 
    ) -> dict | list[dict]:
    """Highlevel funtion that invokes a Cookie class and getting cookies

    Args:
        api (str): An api to connect and a key for a dict with cookies
        not_visible (bool, optional): Starts script in nonvisble mode. Defaults to False.
        cookie_name (str | None, optional): You may choose your own cookie or set None if need to get all. Defaults to 'cf_clearance'.
        timeout (int, optional): A life time of script and time wait till page loads. Defaults to 10.
        safety (bool, optional): more additional parameters to avoid cloudflare. Defaults to False.
        minimaze (bool, optional): minimaze the window size. Defaults to True.

    Returns:
        dict | list[dict]: A single cookie or list of cookies
    """
    return __obj.connect_and_fetch(api=api, not_visible=not_visible, cookie_name=cookie_name, timeout=timeout, safety=safety, minimaze=minimaze)

@sync_to_async
def get_cookie_async(
    api: str, 
    not_visible: bool = False, 
    cookie_name: str | None = 'cf_clearance',  
    timeout: int = 15, 
    safety: bool = False, 
    minimaze: bool = False,
    __obj: Cookie = Cookie(),
    ) -> dict | list[dict]:
    """
    Same to sync version, but nonblocking. Awaitable object
    """
    return __obj.connect_and_fetch(api=api, not_visible=not_visible, cookie_name=cookie_name, timeout=timeout, safety=safety, minimaze=minimaze)

