import json
import pytchat
from pytchat.parser.live import Parser
from pytchat.processors.speed.calculator import SpeedCalculator

parser = Parser(is_replay=False)


def test_speed_1():
    stream = pytchat.create("Hj-wnLIYKjw", seektime = 6000,processor=SpeedCalculator())
    while stream.is_alive():
        speed = stream.get()
        assert speed > 100
        break
test_speed_1()
    