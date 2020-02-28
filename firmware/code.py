import math
import time

import adafruit_dotstar
import board
import busio
from therefore import usb, readkeys, ble
from therefore.writekeys import Output, Layout

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=100)

DEBUG = True
VERBOSE = False

if DEBUG:
    def debug(msg):
        print(msg)
        uart.write((msg + '\r\n').encode('utf-8'))
else:
    def debug(msg):
        pass

if VERBOSE:
    def verbose(msg):
        debug(msg)
else:
    def verbose(msg):
        pass

layout_definition = [
    ['`', '1', '2', '3', '4', '5', 'fn'],
    ['tab', 'q', 'w', 'e', 'r', 't', ' '],
    ['caps_lock', 'a', 's', 'd', 'f', 'g', ' '],
    ['shift', 'z', 'x', 'c', 'v', 'b', ' '],
    ['control', 'win', 'alt', ' ', ' ', ' ', ' '],
    ['backspace', ' ', 'windows'],
]


def reverse(l):
    return list(reversed(l))


layout_definition = reverse([reverse(row) for row in layout_definition])

led = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)
led.brightness = 1


class USBBLESwitchingProcess:
    def __init__(self, usb_keyboard, ble_keyboard, clock_rate=300):
        self.usb_keyboard = usb_keyboard
        self.ble_keyboard = ble_keyboard
        self.clock_rate = clock_rate

        self.previous = set()
        self._state = 'none'
        self.state = 'start'  # also sets output
        self.previous_state = None
        self.advertising = False

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, newval):
        if newval != self._state:
            debug(self._state + ' -> ' + newval)

            if newval == 'ble_connected':
                self.output = self.ble_keyboard()
                led[0] = (0, 0, 255)
            elif newval == 'usb':
                led[0] = (255, 0, 0)
                self.output = self.usb_keyboard()
            elif newval == 'ble_advertising':
                led[0] = (32, 0, 255)
            elif newval == 'start':
                led[0] = (255, 255, 0)

            self._state = newval

    def _check_transitions(self):
        # USB connection overrides everything
        if self.state == 'start':
            if usb.connected():
                self.state = 'usb'
            else:
                self.state = 'ble_unconnected'
        elif self.state != 'usb':
            if usb.connected():
                self.state = 'usb'

    def act(self):
        s = self.state
        if s == 'usb':
            self.handle_usb()
        elif s == 'ble_unconnected':
            self.handle_ble_unconnected()
        elif s == 'ble_advertising':
            self.handle_ble_advertising()
        elif s == 'ble_connected':
            self.handle_ble_connected()

    def handle_usb(self):
        self.handle_keypresses()
        self.output.press()

    def handle_ble_connected(self):
        if not ble.ble.connected:
            self.state = 'start'
            return
        self.handle_keypresses()

    def handle_ble_unconnected(self):
        ble.advertise()
        self.state = 'ble_advertising'

    def handle_ble_advertising(self):
        if ble.ble.connected:
            self.state = 'ble_connected'

    def handle_keypresses(self):
        current = set(readkeys.get_pressed_keys())
        new = current - self.previous
        gone = self.previous - current

        if new:
            verbose('New: %s' % new)
            for kc in new:
                self.output.press(kc)
        if gone:
            verbose('Gone: %s' % gone)
            for kc in gone:
                self.output.release(kc)

        if new | gone:
            verbose('Current: %s' % current)

        self.previous = current

    def run(self):
        while True:
            # following two lines may change state
            self._check_transitions()
            try:
                self.act()
            except OSError:
                self.state = 'start'

    def _set_led_state(self):
        s = self.state
        led.brightness = 1

        if s == 'ble_unconnected':
            # make that sucker smooth blink
            brightness = 0.2 + (0.8 * ((1 + math.sin(time.monotonic() * 10)) / 2))
            red = int(round(32 * brightness))
            blue = int(round(255 * brightness))
            led[0] = (red, 0, blue)

        if self.state == self.previous_state:
            return

        debug(self.state)

        if s == 'start':
            led[0] = (255, 255, 255)
        elif s == 'usb':
            led[0] = (255, 255, 255)
        elif s == 'ble_connected':
            led[0] = (0, 0, 255)


if __name__ == '__main__':
    layout = Layout(layout_definition)


    def get_ble_keyboard():
        return Output(
            layout=layout,
            keyboard=ble.get_keyboard(),
        )


    def get_usb_keyboard():
        return Output(
            layout=layout,
            keyboard=usb.get_keyboard(),
        )


    while True:
        runner = USBBLESwitchingProcess(get_usb_keyboard, get_ble_keyboard)
        runner.run()
