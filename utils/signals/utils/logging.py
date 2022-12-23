import logging
from logging import Logger
from types import NoneType
from typing import Any

from pathlib import Path, PosixPath


def log( 
    msg: str | Any, 
    name: str | None = None,  
    level: str = 'info', 
    file_to_save: str | Path | PosixPath | None = None,
    level_name: bool = True
    ) -> Logger:

    if not isinstance(level, str):
        raise TypeError(f'level should be str type, not {type(level).__name__}')
    if not isinstance(file_to_save, (str, Path, PosixPath, NoneType)):
        raise TypeError(f'file_to_save should be str or pathlike object, not {type(file_to_save).__name__}')

    level = level.lower()
    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
        'exception': logging.ERROR
    }
    if level_name:
        _format = "%(asctime)s %(levelname)s: %(message)s"
    else:
        _format = "%(asctime)s: %(message)s"

    logging.basicConfig(
        format=_format,
        level=levels[level],
        encoding='utf-8',
        filename=str(file_to_save) if file_to_save else None

    )
    logger = logging.getLogger(name)
    _logger = {
        'debug': logger.debug,
        'info': logger.info,
        'warning': logger.warning,
        'error': logger.error,
        'critical': logger.critical,
        'exception': logger.exception
    }
    return _logger[level](msg) # getting an object to invoke with message