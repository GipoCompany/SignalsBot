from .token import Cookie, get_cookie_async, get_cookie_sync

import os, json
from pathlib import PosixPath, Path


__all__ = [
    'get_cookie_sync',
    'Cookie',
    'get_cookie_async'
    'set_cookie'
]


def set_cookie(url: str, path_to_file: Path | PosixPath | str, cookie_name: str | None = None) -> dict:
    if os.path.exists(path_to_file):
            with open(path_to_file, 'r', encoding='utf-8') as file:
                return json.loads(file.read())
    else:
        return get_cookie_sync(api=url, cookie_name=cookie_name, safety=True)