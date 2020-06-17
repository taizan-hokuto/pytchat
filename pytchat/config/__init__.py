from . import mylogger

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}


def logger(module_name: str, loglevel=None):
    module_logger = mylogger.get_logger(module_name, loglevel=loglevel)
    return module_logger
