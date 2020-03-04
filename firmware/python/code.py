import adafruit_dotstar
import board
import busio
import storage

from therefore import usb, readkeys, ble, mesh, layout
from therefore.writekeys import Output, Layout, SystemKeyPressed

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

HAND = storage.getmount('/').label.lower()

keypad = readkeys.Keypad(HAND)

led = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)
led.brightness = 0.3

START = 'start'
MESHING = 'meshing'
MESH_CONNECTED = 'mesh connected'
USB = 'usb'
BLE_CONNECTED = 'ble connected'
BLE_UNCONNECTED = 'ble unconnected'
BLE_ADVERTISING = 'ble advertising'
HERO = 'hero'
HERO_BLE = 'hero ble'
HERO_USB = 'hero usb'
SIDEKICK = 'sidekick'


class MainProcess:
    def __init__(self, usb_keyboard, ble_keyboard, clock_rate=300):
        self.usb_keyboard = usb_keyboard
        self.ble_keyboard = ble_keyboard
        self.clock_rate = clock_rate

        self.previous = set()
        self._state = 'none'
        self.state = START  # also sets output
        self.previous_state = None
        self.advertising = False
        self.pool = mesh.Negotiations(hand=HAND)
        self.remote_keys = None

        self.mode = 'usb_only'

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode = mode
        if mode == 'usb_only':
            self.output = self.usb_keyboard()
        elif mode == 'ble_only':
            self.output = self.ble_keyboard()


    def run(self):
        while True:
            try:
                self.act()
            except OSError:
                self.state = START

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, newval):
        if newval != self._state:
            debug(self._state + ' -> ' + newval)

            if newval == BLE_CONNECTED:
                led[0] = (0, 0, 32)
            elif newval == USB:
                led[0] = (32, 0, 0)
            elif newval == BLE_ADVERTISING:
                led[0] = (4, 0, 32)
            elif newval == START:
                led[0] = (32, 32, 0)

            self._state = newval

    def act(self):
        s = self.state
        getattr(self, 'handle_' + self.state.replace(' ', '_'))()

    def handle_start(self):
        self.state = MESHING

    def handle_meshing(self):
        self.pool.connect()
        self.uart = self.pool.uart
        self.role = self.pool.my_role
        self.state = MESH_CONNECTED

    def handle_mesh_connected(self):
        if self.role == 'batman':
            self.state = HERO
        elif self.role == 'robin':
            self.state = SIDEKICK

    def handle_hero(self):
        if self.mode == 'usb_only':
            self.state = USB
        elif self.mode == 'ble_only':
            self.state = BLE_UNCONNECTED

    def handle_keypresses(self):
        local_pressed = set(keypad.pressed)
        remote_pressed = set(self.uart.keys_pressed)
        current = set(local_pressed) | set(remote_pressed)

        new = current - self.previous
        gone = self.previous - current

        if new:
            verbose('New: %s' % new)
            for kc in new:
                try:
                    self.output.press(kc)
                except SystemKeyPressed as e:
                    self.handle_syskey(e.keycode)
        if gone:
            verbose('Gone: %s' % gone)
            for kc in gone:
                self.output.release(kc)

        if new | gone:
            verbose('Current: %s' % current)

        self.previous = current

    def handle_sidekick(self):
        self.uart.keys_pressed = keypad.pressed

    def handle_usb(self):
        self.handle_keypresses()

    def handle_ble_connected(self):
        if not ble.ble.connected:
            self.state = START
            return
        self.handle_keypresses()

    def handle_ble_unconnected(self):
        ble.advertise()
        self.state = BLE_ADVERTISING

    def handle_ble_advertising(self):
        if ble.connected():
            self.state = BLE_CONNECTED

    def handle_syskey(self, keycode):
        if keycode == 'switch':
            if self.mode == 'usb_only':
                self.mode = 'ble_only'
            elif self.mode == 'ble_only':
                self.mode = 'usb_only'
            self.state = MESH_CONNECTED


if __name__ == '__main__':
    layout = Layout(layout.layout)  # layout


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
        runner = MainProcess(get_usb_keyboard, get_ble_keyboard)
        runner.run()
