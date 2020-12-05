from pytchat.parser.live import Parser
import json
from pytchat.exceptions import NoContents


parser = Parser(is_replay=False)


def _open_file(path):
    with open(path, mode='r', encoding='utf-8') as f:
        return f.read()


def test_finishedlive(*mock):
    _text = _open_file('tests/testdata/finished_live.json')
    _text = json.loads(_text)

    try:
        parser.parse(parser.get_contents(_text)[0])
        assert False
    except NoContents:
        assert True


def test_parsejson(*mock):
    _text = _open_file('tests/testdata/paramgen_firstread.json')
    _text = json.loads(_text)

    try:
        s, _ = parser.parse(parser.get_contents(_text)[0])
        assert s['timeoutMs'] == 5035
        assert s['continuation'] == "0ofMyAPiARp8Q2c4S0RRb0xhelJMZDBsWFQwdERkalFhUTZxNXdiMEJQUW83YUhSMGNITTZMeTkzZDNjdWVXOTFkSFZpWlM1amIyMHZiR2wyWlY5amFHRjBQM1k5YXpSTGQwbFhUMHREZGpRbWFYTmZjRzl3YjNWMFBURWdBZyUzRCUzRCiPz5-Os-PkAjAAOABAAUorCAAQABgAIAAqDnN0YXRpY2NoZWNrc3VtOgBAAEoCCAFQgJqXjrPj5AJYA1CRwciOs-PkAli3pNq1k-PkAmgBggEECAEQAIgBAKABjbfnjrPj5AI%3D"
    except Exception:
        assert False
