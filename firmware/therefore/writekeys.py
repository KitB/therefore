from adafruit_hid.keycode import Keycode

DEFAULT_KEYCODE = Keycode.SPACE

lookups = {
    '1': 'one',
    '2': 'two',
    '3': 'three',
    '4': 'four',
    '5': 'five',
    '6': 'six',
    '7': 'seven',
    '8': 'eight',
    '9': 'nine',
    '0': 'zero',
    '`': 'grave_accent',
    '\'': 'quote',
    ';': 'semicolon',
    ',': 'comma',
    '.': 'period',
    '/': 'forward_slash',
    '[': 'left_bracket',
    ']': 'right_bracket',
    '\\': 'backslash',
    '=': 'equals',
    '-': 'minus',
    'ins': 'insert',
    'del': 'delete',
    'win': 'gui',
    'left': 'left_arrow',
    'right': 'right_arrow',
    'up': 'up_arrow',
    'down': 'down_arrow',
    'caps': 'caps_lock'
}


def lookup_keystr(keystr, default=DEFAULT_KEYCODE):
    keystr = lookups.get(keystr, keystr)
    try:
        return getattr(Keycode, keystr.upper())
    except AttributeError:
        return default


class Layout:
    def __init__(self, definition, default=DEFAULT_KEYCODE):
        self.table = [[lookup_keystr(column) for column in row] for row in definition]
        self.default = default

    def __getitem__(self, loc):
        column, row = loc
        try:
            return self.table[row][column]
        except IndexError:
            return self.default


class Output:
    def __init__(self, layout, keyboard):
        self.keyboard = keyboard
        self.layout = layout

    def press(self, *locations):
        keycodes = [self.layout[loc] for loc in locations]
        self.keyboard.press(*keycodes)

    def release(self, *locations):
        keycodes = [self.layout[loc] for loc in locations]
        self.keyboard.release(*keycodes)
