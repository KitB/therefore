""" Testing the link between layout_handling and writekeys """
import pytest

from therefore import layout, layout_handling, writekeys

from .test_writekeys import RecordingKeeb
from .test_layout_handling import _PUNCFN


@pytest.fixture
def recording_keyboard():
    return RecordingKeeb()


@pytest.fixture
def recording_consumer_control():
    return RecordingKeeb()


@pytest.fixture
def output(recording_keyboard, recording_consumer_control):
    return writekeys.Output(recording_keyboard, recording_consumer_control)


@pytest.fixture(scope='session')
def parsed_layout():
    return layout_handling.parse_layout(layout.layout['layers'])


@pytest.fixture
def layout_handler(parsed_layout, output):
    return layout_handling.LayoutHandler(parsed_layout, output.press, output.release)

def test_basic_typing(layout_handler, recording_keyboard):
    layout_handler.press(1, 0)
    layout_handler.release(1, 0)
    assert recording_keyboard.calls == [('press', 30), ('release', 30)]

def test_combo(layout_handler, recording_keyboard):
    layout_handler.press(*_PUNCFN)
    layout_handler.press(11, 2)
    assert [set(call) for call in recording_keyboard.calls] == [{'press', 38, 225}]

def test_sequence(layout_handler, recording_keyboard):
    layout_handler.press(15, 5)
    layout_handler.release(15, 5)
    assert recording_keyboard.calls == \
           [
               ('press', 82),
               ('press', 82),
               ('press', 81),
               ('press', 81),
               ('press', 80),
               ('press', 79),
               ('press', 80),
               ('press', 79),
               ('press', 5),
               ('press', 4),
               ('press', 40),

               ('release', 82),
               ('release', 82),
               ('release', 81),
               ('release', 81),
               ('release', 80),
               ('release', 79),
               ('release', 80),
               ('release', 79),
               ('release', 5),
               ('release', 4),
               ('release', 40),
           ]
