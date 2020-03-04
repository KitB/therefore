import adafruit_matrixkeypad
import board
import digitalio

col_pins = [board.A0, board.A1, board.A2, board.A3, board.A4, board.A5, board.SCK]
row_pins = [board.D7, board.D9, board.D10, board.D11, board.D12, board.D13]


class Keypad:
    def __init__(self, hand, col_pins=col_pins, row_pins=row_pins):
        width = len(col_pins)
        height = len(row_pins)
        rows = [digitalio.DigitalInOut(x) for x in row_pins]
        cols = [digitalio.DigitalInOut(x) for x in col_pins]
        if hand == 'left':
            keys = [[(column, row) for column in range(width)] for row in range(height)]
        elif hand == 'right':
            keys = [[(13 - column, row) for column in range(7)] for row in range(height)]
        else:
            keys = []

        self.keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

    @property
    def pressed(self):
        return self.keypad.pressed_keys
