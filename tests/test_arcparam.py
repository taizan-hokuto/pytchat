import json
import httpx
import pytchat.config as config
from pytchat.paramgen import arcparam
from pytchat.parser.live import Parser


def test_arcparam_0(mocker):
    param = arcparam.getparam("01234567890", -1)
    assert param == "op2w0wSDARpsQ2pnYURRb0xNREV5TXpRMU5qYzRPVEFxSndvWVgxOWZYMTlmWDE5ZlgxOWZYMTlmWDE5ZlgxOWZYMTlmRWdzd01USXpORFUyTnpnNU1Cb1Q2cWpkdVFFTkNnc3dNVEl6TkRVMk56ZzVNQ0FCKOgHMAA4AEAASARSAiAAcgIIAXgA" 


def test_arcparam_1(mocker):
    param = arcparam.getparam("01234567890", seektime=100000)
    assert param == "op2w0wSHARpsQ2pnYURRb0xNREV5TXpRMU5qYzRPVEFxSndvWVgxOWZYMTlmWDE5ZlgxOWZYMTlmWDE5ZlgxOWZYMTlmRWdzd01USXpORFUyTnpnNU1Cb1Q2cWpkdVFFTkNnc3dNVEl6TkRVMk56ZzVNQ0FCKIDQ28P0AjAAOABAAEgDUgIgAHICCAF4AA%3D%3D"

def test_arcparam_3(mocker):
    param = arcparam.getparam("01234567890")
    assert param == "op2w0wSDARpsQ2pnYURRb0xNREV5TXpRMU5qYzRPVEFxSndvWVgxOWZYMTlmWDE5ZlgxOWZYMTlmWDE5ZlgxOWZYMTlmRWdzd01USXpORFUyTnpnNU1Cb1Q2cWpkdVFFTkNnc3dNVEl6TkRVMk56ZzVNQ0FCKOgHMAA4AEAASARSAiAAcgIIAXgA"
