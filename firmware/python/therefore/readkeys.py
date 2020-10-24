import board
import digitalio
from digitalio import Direction, Pull

col_pins = [board.A0, board.A1, board.A2, board.A3, board.A4, board.A5, board.SCK, board.MOSI]
row_pins = list(reversed([board.D6, board.D9, board.D10, board.D11, board.D12, board.D13]))


class MatrixKeypad(object):
    """Driver for passive matrix keypads - any size"""
    def __init__(self, row_pins, col_pins, keys):
        """Initialise the driver with the correct size and key list.

        :param list row_pins: a list of DigitalInOut objects corresponding to the rows
        :param list col_pins: a list of DigitalInOut objects corresponding to the colums
        :param list keys: a list of lists that has the corresponding symbols for each key
        """
        if len(keys) != len(row_pins):
            raise RuntimeError("Key name matrix doesn't match # of columns")
        for row in keys:
            if len(row) != len(col_pins):
                raise RuntimeError("Key name matrix doesn't match # of rows")
        self.row_pins = row_pins
        self.col_pins = col_pins
        self.keys = keys

    @property
    def pressed_keys(self):
        """An array containing all detected keys that are pressed from the initalized
        list-of-lists passed in during creation"""
        # make a list of all the keys that are detected
        pressed = []

        # set all pins pins to be inputs w/pullups
        for pin in self.row_pins+self.col_pins:
            pin.direction = Direction.INPUT
            pin.pull = Pull.UP

        for col in range(len(self.col_pins)):
            # set one column low at a time
            self.col_pins[col].direction = Direction.OUTPUT
            self.col_pins[col].value = False
            # check the row pins, which ones are pulled down
            for row in range(len(self.row_pins)):
                if not self.row_pins[row].value:
                    pressed.append(self.keys[row][col])
            # reset the pin to be an input
            self.col_pins[col].direction = Direction.INPUT
            self.col_pins[col].pull = Pull.UP
        return pressed

class Keypad:
    def __init__(self, hand, col_pins=col_pins, row_pins=row_pins):
        width = len(col_pins)
        height = len(row_pins)
        rows = [digitalio.DigitalInOut(x) for x in row_pins]
        cols = [digitalio.DigitalInOut(x) for x in col_pins]

        if hand == 'left':
            keys = [[(column, row) for column in range(width)] for row in range(height)]
        elif hand == 'right':
            keys = [[(15 - column, row) for column in range(width)] for row in range(height)]
        else:
            keys = []

        self.keypad = MatrixKeypad(rows, cols, keys)

    @property
    def pressed(self):
        return self.keypad.pressed_keys
