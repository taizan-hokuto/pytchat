import pytest
from pytchat.paramgen import liveparam

def test_liveparam_0(mocker):
    _ts1= 1546268400
    param = liveparam._build("01234567890",
    *([_ts1*1000000 for i in range(5)]), topchat_only=False)
    test_param="0ofMyANcGhxDZzhLRFFvTE1ERXlNelExTmpjNE9UQWdBUT09KIC41tWqyt8CQAFKC1CAuNbVqsrfAlgDUIC41tWqyt8CWIC41tWqyt8CaAGCAQIIAZoBAKABgLjW1arK3wI%3D"
    assert test_param == param