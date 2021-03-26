from adafruit_hid.keyboard import Keyboard
from therefore.cc_device import ConsumerControl
import usb_hid


def get_keyboard():
    return Keyboard(usb_hid.devices)


def get_consumer_control():
    return ConsumerControl(usb_hid.devices)


def connected():
    try:
        get_keyboard()
    except OSError:
        return False
    else:
        return True
