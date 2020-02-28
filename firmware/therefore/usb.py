from adafruit_hid.keyboard import Keyboard
import usb_hid


def get_keyboard():
    return Keyboard(usb_hid.devices)


def connected():
    try:
        get_keyboard()
    except OSError:
        return False
    else:
        return True
