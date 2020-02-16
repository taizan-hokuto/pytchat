import logging
from . import mylogger

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}

def logger(module_name: str, loglevel = logging.DEBUG):
    module_logger = mylogger.get_logger(module_name, loglevel = loglevel)
    return module_logger


