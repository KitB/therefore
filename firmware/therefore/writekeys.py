import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode


DEFAULT_KEYCODE = Keycode.SPACE


lookups = {
    '1': 'one',
    '2': 'two',
    '3': 'three',
    '4': 'four',
    '5': 'five',
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
