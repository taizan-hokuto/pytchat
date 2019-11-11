import pytest
from pytchat.core_multithread.parser import Parser
import pytchat.config as config
import requests, json
from pytchat.paramgen import liveparam

def test_liveparam_0(mocker):
    _ts1= 1546268400
    param = liveparam._build("01234567890",
    *([_ts1*1000000 for i in range(5)]))
    test_param="0ofMyAPiARp8Q2c4S0RRb0xNREV5TXpRMU5qYzRPVEFhUTZxNXdiMEJQUW83YUhSMGNITTZMeTkzZDNjdWVXOTFkSFZpWlM1amIyMHZiR2wyWlY5amFHRjBQM1k5TURFeU16UTFOamM0T1RBbWFYTmZjRzl3YjNWMFBURWdBZyUzRCUzRCiAuNbVqsrfAjAAOABAAkorCAEQABgAIAAqDnN0YXRpY2NoZWNrc3VtOgBAAEoCCAFQgLjW1arK3wJYA1CAuNbVqsrfAliAuNbVqsrfAmgBggEECAEQAIgBAKABgLjW1arK3wI%3D"
    assert test_param == param