import adafruit_matrixkeypad
import board
import digitalio

cols = [digitalio.DigitalInOut(x) for x in [board.A0, board.A1, board.A2, board.A3, board.A4, board.A5, board.D2]]

rows = [digitalio.DigitalInOut(x) for x in [board.D7, board.D9, board.D10, board.D11, board.D12, board.D13]]

keys = [[(column, row) for column in range(7)] for row in range(6)]

keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

def get_pressed_keys():
    return keypad.pressed_keys
