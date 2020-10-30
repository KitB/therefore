import struct

import adafruit_ble as ble
import board
import busio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.characteristics import ComplexCharacteristic
from adafruit_ble.characteristics.int import Uint8Characteristic
from adafruit_ble.services.nordic import UARTService
from adafruit_ble.uuid import VendorUUID


# TODO: encrypt the connection

class BoundPressedKeySet:
    def __init__(self, bound_keyset):
        self.bound_keyset = bound_keyset

    @property
    def pressed(self):
        bites = self.bound_keyset.value
        return list(zip(bites, bites[1:]))

    @pressed.setter
    def pressed(self, locations):
        fmt = 'B' * 2 * len(locations)
        self.bound_keyset.value = struct.pack(fmt, *[v for loc in locations for v in loc])


class PressedKeySet(ComplexCharacteristic):
    def bind(self, service):
        bound_characteristic = super().bind(service)
        return BoundPressedKeySet(bound_characteristic)


class SubkeypadService(UARTService):
    uuid = VendorUUID('39A00001-C17A-7AE2-EA02-A50E24DCCA9E')
    left_state = Uint8Characteristic(
        uuid=VendorUUID('39A00003-C1AB-74A2-EFA2-E50EA4DCCA9E')
    )
    right_state = Uint8Characteristic(
        uuid=VendorUUID('39A00004-C1AB-74A2-EFA2-E50EA4DCCA9E')
    )


radio = ble.BLERadio()


class BaseNegotiations:
    def __init__(self, hand):
        self.hand = hand

    @property
    def my_role(self):
        if self.hand == 'left':
            return 'batman'
        elif self.hand == 'right':
            return 'robin'


class WiredNegotiations(BaseNegotiations):
    def __init__(self, *, hand):
        super().__init__(hand)
        self.uart = UARTWrapper(busio.UART(board.TX, board.RX, baudrate=9600, timeout=100))

    def connect(self):
        pass

class Negotiations(BaseNegotiations):
    def __init__(self, *, hand):
        super().__init__(hand)
        self.usb_connected = False
        self.skp_service = SubkeypadService()
        self.advert = ProvideServicesAdvertisement(self.skp_service)
        self.connection = None

    def connect_left(self):
        print('advertising')
        radio.start_advertising(self.advert)
        while not (self.connection and self.connection.connected):
            for connection in radio.connections:
                if SubkeypadService in connection:
                    self._set_connection()
        radio.stop_advertising()
        print('done advertising')

    def connect_right(self):
        print('searching')
        for ad in radio.start_scan(ProvideServicesAdvertisement, interval=0.02, window=0.02):
            if SubkeypadService in ad.services:
                self.connection = radio.connect(ad)
                self.connection.connection_interval = 7.5
                break
        radio.stop_scan()
        self._set_connection()
        print('done searching')

    def _set_connection(self):
        for connection in radio.connections:
            if SubkeypadService in connection:
                self.connection = connection
        self.uart = UARTWrapper(self.skp)

    @property
    def skp(self):
        """ SubkeypadService"""
        if not self.connection.connected:
            return None
        if self.hand == 'right':
            return self.connection[SubkeypadService]
        elif self.hand == 'left':
            return self.skp_service

    def connect(self):
        if self.hand == 'right':
            self.connect_right()
        elif self.hand == 'left':
            self.connect_left()


class UARTWrapper:
    def __init__(self, uart):
        self.uart = uart
        self.last = []

    @property
    def keys_pressed(self):
        if not self.uart.in_waiting:
            return self.last
        self.uart.readline()
        bites = self.uart.read(24)
        self.uart.reset_input_buffer()

        locs = struct.unpack('b' * 24, bites)

        def _gen():
            for i in range(0, len(locs), 2):
                if locs[i] >= 0:
                    yield (locs[i], locs[i + 1])

        self.last = list(_gen())
        return self.last

    @keys_pressed.setter
    def keys_pressed(self, locs):
        n = len(locs)

        send_locs = [(-1, -1)] * 12
        send_locs[0:n] = locs

        fmt = 'b' * 24
        b = struct.pack(fmt, *[v for loc in send_locs for v in loc])
        self.uart.write(b'\n' + b)
