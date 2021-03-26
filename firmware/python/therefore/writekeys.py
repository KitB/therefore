from therefore.cc_device import ConsumerControl
from adafruit_hid.keyboard import Keyboard


class Output:
    """ Converts action-outputs from the layout handling to actual actions.

    press and release are expected to be passed in as the emit functions to a LayoutHandler
    """
    def __init__(self, keyboard: Keyboard, consumer_control: ConsumerControl):
        self.keyboard = keyboard
        self.consumer_control = consumer_control

    def press(self, action):
        command, args = action
        getattr(self, 'handle_{}_pressed'.format(command))(args)

    def release(self, action):
        command, args = action
        getattr(self, 'handle_{}_released'.format(command))(args)

    def handle_key_pressed(self, keycode):
        self.keyboard.press(keycode)

    def handle_key_released(self, keycode):
        self.keyboard.release(keycode)

    def handle_consumer_control_pressed(self, cc_code):
        self.consumer_control.press(cc_code)

    def handle_consumer_control_released(self, cc_code):
        self.consumer_control.release()

    def handle_combo_pressed(self, keys):
        self.keyboard.press(*(code for mode, code in keys if mode == 'key'))

    def handle_combo_released(self, keys):
        self.keyboard.release(*(code for mode, code in keys if mode == 'key'))

    def handle_sequence_pressed(self, actions):
        for action in actions:
            self.press(action)

    def handle_sequence_released(self, actions):
        for action in actions:
            self.release(action)
