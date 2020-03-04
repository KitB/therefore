import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_ble.services.standard.hid import HIDService
from adafruit_hid.keyboard import Keyboard

from . import mesh

hid = HIDService()

device_info = DeviceInfoService(software_revision=adafruit_ble.__version__,
                                manufacturer="Adafruit Industries")
advertisement = ProvideServicesAdvertisement(hid)
advertisement.appearance = 961
scan_response = Advertisement()
scan_response.complete_name = "Therefore"

ble = adafruit_ble.BLERadio()


def get_keyboard():
    return Keyboard(hid.devices)


def advertise():
    if not connected():
        print("advertising")
        ble.start_advertising(advertisement, scan_response)
    else:
        print("already connected")

def disconnect():
    for con in ble.connections:
        con.disconnect()

def connected():
    for connection in ble.connections:
        if mesh.SubkeypadService not in connection:
            return True
    return False
