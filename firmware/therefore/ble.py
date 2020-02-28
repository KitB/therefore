import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_ble.services.standard.hid import HIDService
from adafruit_hid.keyboard import Keyboard

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
    if not ble.connected:
        print("advertising")
        ble.start_advertising(advertisement, scan_response)
    else:
        print("already connected")
        print(ble.connections)

def disconnect():
    for con in ble.connections:
        con.disconnect()
