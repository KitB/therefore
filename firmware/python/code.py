import board
import busio
import storage
import neopixel

from therefore import usb, readkeys, ble, mesh, layout, layout_handling
from therefore.layout_handling import LayoutHandler, parse_layout
from therefore.writekeys import Output

from _bleio import ConnectionError

DEBUG = True
VERBOSE = False

if DEBUG:
    def debug(msg):
        print(msg)
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
for entry in storage.getmount('/').ilistdir('/'):
    if entry[0].lower() == 'left':
        HAND = 'left'

keypad = readkeys.Keypad(HAND)

led = neopixel.NeoPixel(board.NEOPIXEL, 1, pixel_order=neopixel.GRB)
led.brightness = 0.01


# TODO: battery charge tracking

# this would be an enum but circuitpython doesn't implement them.
class State:
    none = 'none'
    start = 'start'
    meshing = 'meshing'
    mesh_connected = 'mesh connected'
    usb = 'usb'
    ble_connected = 'ble connected'
    ble_unconnected = 'ble unconnected'
    ble_advertising = 'ble advertising'
    hero = 'hero'
    sidekick = 'sidekick'


class MainProcess:
    def __init__(self, usb_handler, ble_handler, clock_rate=300):
        self.usb_handler = usb_handler
        self.ble_handler = ble_handler
        self.clock_rate = clock_rate

        self.previous = set()
        self._state = State.none
        self.previous_state = None
        self.state = State.start  # also sets handler
        self.advertising = False
        self.pool = mesh.WiredNegotiations(hand=HAND)
        self.remote_keys = None

        self.mode = 'usb_only'

    def run(self):
        while True:
            try:
                self.act()
            except (OSError, IndexError, ConnectionError, ValueError) as e:
                import sys
                print('=' * 80)
                sys.print_exception(e)
                self.state = State.start

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, newval: str):
        if newval != self._state:
            debug(self._state + ' -> ' + newval)

            if newval == State.ble_connected:
                led[0] = (0, 0, 255)
                self.handler = self.ble_handler()
            elif newval == State.usb:
                led[0] = 0x00_FF_00
                self.handler = self.usb_handler()
            elif newval == State.ble_advertising:
                led[0] = (32, 0, 255)
            elif newval == State.start:
                led[0] = (32, 32, 0)
            elif newval == State.sidekick:
                led[0] = 0xFF_FF_FF

            self._state = newval

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode = mode

    def act(self):
        s = self.state
        getattr(self, 'handle_' + self.state.replace(' ', '_'))()

    def handle_start(self):
        self.state = State.meshing

    def handle_meshing(self):
        self.pool.connect()
        self.uart = self.pool.uart
        self.role = self.pool.my_role
        self.state = State.mesh_connected

    def handle_mesh_connected(self):
        if self.role == 'batman':
            self.state = State.hero
        elif self.role == 'robin':
            self.state = State.sidekick

    def handle_hero(self):
        if self.mode == 'usb_only':
            self.state = State.usb
        elif self.mode == 'ble_only':
            self.state = State.ble_unconnected

    def handle_keypresses(self):
        local_pressed = set(keypad.pressed)
        remote_pressed = set(self.uart.keys_pressed)
        current = set(local_pressed) | set(remote_pressed)

        new = current - self.previous
        gone = self.previous - current

        if new:
            verbose('New: %s' % new)
            for x, y in new:
                self.handler.press(x, y)
                # TODO: removed syskey handling from here, need to add back in for :switch
        if gone:
            verbose('Gone: %s' % gone)
            for x, y in gone:
                self.handler.release(x, y)

        if new | gone:
            verbose('Current: %s' % current)

        self.previous = current

    def handle_sidekick(self):
        self.uart.keys_pressed = keypad.pressed

    def handle_usb(self):
        self.handle_keypresses()

    def handle_ble_connected(self):
        if not ble.ble.connected:
            self.state = State.start
            return
        self.handle_keypresses()

    def handle_ble_unconnected(self):
        ble.advertise()
        self.state = State.ble_advertising

    def handle_ble_advertising(self):
        if ble.connected():
            self.state = State.ble_connected

    def handle_syskey(self, keycode):
        if keycode == 'switch':
            if self.mode == 'usb_only':
                self.mode = 'ble_only'
            elif self.mode == 'ble_only':
                self.mode = 'usb_only'
            self.state = State.mesh_connected


if __name__ == '__main__':
    parsed_layout = parse_layout(layout.layout['layers'])


    def get_ble_keyboard():
        output = Output(
            keyboard=ble.get_keyboard(),
            consumer_control=ble.get_consumer_control(),
        )
        return LayoutHandler(
            parsed_layout=parsed_layout,
            emit_press_callable=output.press,
            emit_release_callable=output.release,
        )


    def get_usb_keyboard():
        output = Output(
            keyboard=usb.get_keyboard(),
            consumer_control=usb.get_consumer_control(),
        )
        return LayoutHandler(
            parsed_layout=parsed_layout,
            emit_press_callable=output.press,
            emit_release_callable=output.release,
        )


    while True:
        try:
            runner = MainProcess(get_usb_keyboard, get_ble_keyboard)
        except OSError as e:
            led[0] = (255, 255, 255, 1)
            break
        try:
            runner.run()
        except OSError as e:
            led[0] = (255, 0, 255, 1)

    while True:
        pass
