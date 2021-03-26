import pytest
from therefore import layout, layout_handling
from adafruit_hid.keycode import Keycode


# TODO: dedicated test layout rather than just using my own layout

def test_parse_layout():
    layout_handling.parse_layout(layout.layout['layers'])


class RecordingEmitters:
    def __init__(self):
        self.called_withs = []

    def press(self, *args, **kwargs):
        self.called_withs.append(('press', *args))

    def release(self, *args, **kwargs):
        self.called_withs.append(('release', *args))


@pytest.fixture
def recording_emitters():
    return RecordingEmitters()


@pytest.fixture(scope='session')
def parsed_layout():
    return layout_handling.parse_layout(layout.layout['layers'])


@pytest.fixture
def layout_handler(parsed_layout, recording_emitters):
    return layout_handling.LayoutHandler(parsed_layout, recording_emitters.press, recording_emitters.release)


_LPAREN = ('combo', {('key', Keycode.NINE), ('key', Keycode.SHIFT)})
_PUNCFN = (6, 4)
_FN = (6, 2)
_LSHIFT = (0, 3)
test_data = {
    'vacuous': ([], []),
    'press anything': (
        [('press', (1, 0))],
        [('press', ('key', 30))]),
    'layer change emits nothing': (
        [('press', (6, 4))],
        []
    ),
    'punctuation layer release fn first': (
        [('press', _PUNCFN), ('press', (11, 2)), ('release', _PUNCFN), ('release', (11, 2))],
        [('press', _LPAREN), ('release', _LPAREN)]
    ),
    'punctuation layer release key first': (
        [('press', _PUNCFN), ('press', (11, 2)), ('release', (11, 2)), ('release', _PUNCFN)],
        [('press', _LPAREN), ('release', _LPAREN)]
    ),
    'fns layer combination': (
        [
            ('press', _LSHIFT),
            ('press', _FN),
            ('press', (10, 0)),
            ('release', (10, 0)),
            ('release', _LSHIFT),
            ('release', _FN)
        ],
        [
            ('press', ('key', Keycode.SHIFT)),
            ('press', ('key', Keycode.F6)),
            ('release', ('key', Keycode.F6)),
            ('release', ('key', Keycode.SHIFT))
        ]
    ),
    'switch command': (
        [('press', (9, 0)), ('release', (9, 0))],
        [('press', ('switch', [])), ('release', ('switch', []))]
    ),
    'toggle layer': (
        [
            # Toggle FN
            ('press', _PUNCFN),
            ('press', _FN),
            ('release', _FN),
            ('release', _PUNCFN),

            # Press F1
            ('press', (1, 0)),
            ('release', (1, 0)),

            # Untoggle FN
            ('press', _PUNCFN),
            ('press', _FN),
            ('release', _FN),
            ('release', _PUNCFN),

            # Press numeric 1
            ('press', (1, 0)),
            ('release', (1, 0)),
        ],
        [
            ('press', ('key', Keycode.F1)),
            ('release', ('key', Keycode.F1)),
            ('press', ('key', Keycode.ONE)),
            ('release', ('key', Keycode.ONE)),
        ]
    ),
    'transparent passthrough': (
        [
            ('press', _PUNCFN),
            # Press numeric 1
            ('press', (1, 0)),
            ('release', (1, 0)),
            ('release', _PUNCFN),
        ],
        [
            ('press', ('key', Keycode.ONE)),
            ('release', ('key', Keycode.ONE)),
        ]
    )
}


@pytest.mark.parametrize("input_sequence,expected_output_sequence", test_data.values(), ids=test_data.keys())
def test_example_layout(input_sequence, expected_output_sequence, layout_handler, recording_emitters):
    for direction, (x, y) in input_sequence:
        if direction[0] in ['u', 'r']:
            layout_handler.release(x, y)
        elif direction[0] in ['d', 'p']:
            layout_handler.press(x, y)

    assert recording_emitters.called_withs == expected_output_sequence
