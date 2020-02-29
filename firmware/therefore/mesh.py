import adafruit_ble as ble
import struct
import time
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.characteristics import ComplexCharacteristic
from adafruit_ble.characteristics.int import Uint8Characteristic
from adafruit_ble.services import Service
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


class Negotiations:
    def __init__(self, *, hand):
        self.hand = hand
        self.usb_connected = False
        self.skp_service = SubkeypadService()
        self.advert = ProvideServicesAdvertisement(self.skp_service)
        self.connection = None

    @property
    def my_role(self):
        if self.hand == 'right':
            return 'batman'
        elif self.hand == 'left':
            return 'robin'

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
        for ad in radio.start_scan(ProvideServicesAdvertisement):
            if SubkeypadService in ad.services:
                radio.connect(ad)
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

    @property
    def keys_pressed(self):
        n = self.uart.read(1)[0]
        bites = self.uart.read(2 * n)
        self.uart.reset_input_buffer()

        def _gen():
            for i in range(0, len(bites), 2):
                yield (bites[i], bites[i + 1])
        return list(_gen())

    @keys_pressed.setter
    def keys_pressed(self, locs):
        n = len(locs)
        fmt = 'B' * ((2 * n) + 1)
        b = struct.pack(fmt, n, *[v for loc in locs for v in loc])
        self.uart.write(b)

