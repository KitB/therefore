import adafruit_matrixkeypad
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

cols = [digitalio.DigitalInOut(x) for x in [board.A0, board.A1, board.A2, board.A3, board.A4, board.A5, board.D2]]

rows = [digitalio.DigitalInOut(x) for x in [board.D7, board.D9, board.D10, board.D11, board.D12, board.D13]]

keys = [[(column, row) for column in range(7)] for row in range(6)]

keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

keyboard = Keyboard(usb_hid.devices)

layout = [
    ['`', '1', '2', '3', '4', '5', 'fn'],
    ['tab', 'q', 'w', 'e', 'r', 't', ' '],
    ['caps_lock', 'a', 's', 'd', 'f', 'g', ' '],
    ['shift', 'z', 'x', 'c', 'v', 'b', ' '],
    ['control', 'win', 'alt'],
    ['backspace', ' ', 'windows'],
]

lookups = {
    '1': 'one',
    '2': 'two',
    '3': 'three',
    '4': 'four',
    '5': 'five',
}


def reverse(l):
    return list(reversed(l))


def do_all_lookups(layout):
    return [[lookups.get(column, column) for column in row] for row in layout]


layout = do_all_lookups(reverse([reverse(row) for row in layout]))


def get_layout_loc(loc, default=' '):
    column, row = loc
    try:
        return layout[row][column]
    except IndexError:
        return default


def get_pressed_keycode(loc, default=Keycode.SPACE):
    str_code = get_layout_loc(loc)
    try:
        return getattr(Keycode, str_code.upper())
    except AttributeError:
        return default


def handle_keydown(loc):
    keycode = get_pressed_keycode(loc)
    keyboard.press(keycode)


def handle_keyup(loc):
    keycode = get_pressed_keycode(loc)
    keyboard.release(keycode)


if __name__ == '__main__':
    previous = set()
    while True:
        current = set(keypad.pressed_keys)
        new = current - previous
        gone = previous - current

        for loc in new:
            handle_keydown(loc)

        for loc in gone:
            handle_keyup(loc)

        previous = current
