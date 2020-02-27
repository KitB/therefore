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
scan_response.complete_name = "CircuitPython HID"

ble = adafruit_ble.BLERadio()

keyboard = Keyboard(hid.devices)


def await_ble():
    if not ble.connected:
        print("advertising")
        ble.start_advertising(advertisement, scan_response)
    else:
        print("already connected")
        print(ble.connections)
    while not ble.connected:
        pass

# while True:
#     while not ble.connected:
#         pass
#     print("Start typing:")
#
#     while ble.connected:
#         if not button_1.value:  # pull up logic means button low when pressed
#             # print("back")  # for debug in REPL
#             k.send(Keycode.BACKSPACE)
#             time.sleep(0.1)
#
#         if not button_2.value:
#             kl.write("Bluefruit")  # use keyboard_layout for words
#             time.sleep(0.4)
#
#         if not button_3.value:
#             k.send(Keycode.SHIFT, Keycode.L)  # add shift modifier
#             time.sleep(0.4)
#
#         if not button_4.value:
#             kl.write("e")
#             time.sleep(0.4)
#
#         if not button_5.value:
#             k.send(Keycode.ENTER)
#             time.sleep(0.4)
#
#     ble.start_advertising(advertisement)
