import logging  # noqa
from . import mylogger
from base64 import a85decode as dc
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63,gzip(gfe)',
}
m_headers = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36 Edg/91.0.864.59',
}
_sml = dc(b"BQS?8F#ks-GB\\6`H#IhIF^eo7@rH3;H#IhIF^eor06T''Ch\\'(?XmbXF>%9<FC/iuG%G#jBOQ!ICLqcS5tQB2;gCZ)?UdXC;f$GR3)MM2<(0>O7mh!,G@+K5?SO9T@okV").decode()
_smr = dc(b"BQS?8F#ks-GB\\6`H#IhIF^eo7@rH3;H#IhIF^eor06T''Ch\\'(?XmbXF>%9<FC/iuG%G#jBOQ!iEb03+@<k(QAU-F)8U=fDGsP557S5F7CiNH7;)D3N77^*B6YU@\\?WfBr0emZX=#^").decode()


def logger(module_name: str, loglevel=None):
    module_logger = mylogger.get_logger(module_name, loglevel=loglevel)
    return module_logger
