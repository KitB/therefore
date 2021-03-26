import pytest

from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode

from therefore.writekeys import Output


class RecordingKeeb:
    def __init__(self):
        self.calls = []

    def press(self, *args):
        self.calls.append(('press', *args))

    def release(self, *args):
        self.calls.append(('release', *args))


@pytest.fixture
def recording_keyboard():
    return RecordingKeeb()


@pytest.fixture
def recording_consumer_control():
    return RecordingKeeb()


@pytest.fixture
def output(recording_keyboard, recording_consumer_control):
    return Output(recording_keyboard, recording_consumer_control)


def test_basic_typing(output, recording_keyboard):
    output.press(('key', Keycode.A))
    output.release(('key', Keycode.A))
    assert recording_keyboard.calls == [('press', Keycode.A), ('release', Keycode.A)]


def test_basic_mediakeys(output, recording_consumer_control):
    output.press(('consumer_control', ConsumerControlCode.MUTE))
    output.release(('consumer_control', ConsumerControlCode.MUTE))
    assert recording_consumer_control.calls == [('press', ConsumerControlCode.MUTE), ('release',)]


def test_combo_keys(output, recording_keyboard):
    output.press(('combo', {('key', 38), ('key', 40)}))
    assert [set(call) for call in recording_keyboard.calls] == [{'press', 40, 38}]
