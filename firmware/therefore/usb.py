from adafruit_hid.keyboard import Keyboard
import usb_hid

keyboard = Keyboard(usb_hid.devices)