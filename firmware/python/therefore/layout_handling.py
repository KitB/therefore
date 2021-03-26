"""
Parsing and "execution" of multi-layer layouts.
"""
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode

# TODO: per-country lookups
lookups = {
    ' ': 'spacebar',
    '1': 'one',
    '2': 'two',
    '3': 'three',
    '4': 'four',
    '5': 'five',
    '6': 'six',
    '7': 'seven',
    '8': 'eight',
    '9': 'nine',
    '0': 'zero',
    '`': 'grave_accent',
    '\'': 'quote',
    ';': 'semicolon',
    ',': 'comma',
    '.': 'period',
    '/': 'forward_slash',
    '[': 'left_bracket',
    ']': 'right_bracket',
    '#': 'pound',
    '~': {'shift', 'pound'},
    '\\': 'keypad_backslash',
    '=': 'equals',
    '-': 'minus',
    'ins': 'insert',
    'del': 'delete',
    'esc': 'escape',
    'win': 'gui',
    'left': 'left_arrow',
    'right': 'right_arrow',
    'up': 'up_arrow',
    'down': 'down_arrow',
    'caps': 'caps_lock',

    # media controls
    'prev_track': 'cc_scan_previous_track',
    'next_track': 'cc_scan_next_track',
    'playpause': 'cc_play_pause',
    'louder': 'cc_volume_increment',
    'softer': 'cc_volume_decrement',
    'mute': 'cc_mute',

    # shifted punctuation
    '(': {'shift', 'nine'},
    ')': {'shift', 'zero'},
    '_': {'shift', '-'},
    '^': {'shift', 'six'},
    '&': {'shift', 'seven'},
    '*': {'shift', 'eight'},
    'konami': ['up', 'up', 'down', 'down', 'left', 'right', 'left', 'right', 'b', 'a', 'enter'],
}


def parse_syskey(keystr):
    # syskeys are things that interact with the keyboard itself
    # e.g. changing modes, layers
    keystr = keystr.replace(')', '')
    command, _, argstr = keystr[1:].partition('(')
    args = argstr.split(',') if argstr else []
    return command, args


def parse_consumer_control(keystr):
    # media control buttons, basically
    keystr = keystr[3:]  # strip the 'CC_'

    # let the potential AttributeError through so typos are caught early
    code = getattr(ConsumerControlCode, keystr.upper())

    return 'consumer_control', code


def parse(keystr):
    # check for defined aliases
    keystr = lookups.get(keystr, keystr)

    # list means type them in order
    if isinstance(keystr, list):
        return 'sequence', [parse(k) for k in keystr]

    # set means treat one key as many (but press modifiers first)
    if isinstance(keystr, set):
        return 'combo', {parse(k) for k in keystr}

    # check for system keys
    if keystr[0] == ':':
        # TODO: check that syskey commands are valid
        return parse_syskey(keystr)

    # check for consumer control keys
    if keystr.lower().startswith('cc_'):
        return parse_consumer_control(keystr)

    # finally it must be a standard keycode
    # again ignoring potential AttributeErrors so typos are caught early
    return 'key', getattr(Keycode, keystr.upper())


def parse_layout(layers_dict):
    """ Read a text-based layout dict and return a similar dict of classes and numeric keycodes.

     Verifies along the way.
    """

    def parse_layer(layer_definition):
        return [[parse(keystr) for keystr in row] for row in layer_definition]

    return {name: parse_layer(definition) for name, definition in layers_dict.items()}


class LayerStack:
    def __init__(self):
        #                type         name
        self._stack = [('permanent', 'default')]

    def to(self, layer_name):
        self._stack.insert(0, ('to', layer_name))

    def un_to(self, layer_name):
        self._stack.remove(('to', layer_name))

    def toggle(self, layer_name):
        entry = ('toggle', layer_name)
        if entry in self._stack:
            self._stack.remove(entry)
        else:
            self._stack.insert(0, ('toggle', layer_name))

    @property
    def enabled_layers(self):
        return (layer_name for mode, layer_name in self._stack)

    @property
    def current(self):
        return self._stack[0][1]


LAYER_COMMANDS = {'to', 'toggle'}


class LayoutHandler:
    """ Takes physical key presses/releases and converts them into actions, taking layers into account.

    May in future handle time passing while keys are pressed (e.g. QMK-style mod-tap keys or tap dance).
    """

    @classmethod
    def parse(cls, layers_dict, *args, **kwargs):
        return cls(parse_layout(layers_dict), *args, **kwargs)

    def __init__(self, parsed_layout, emit_press_callable, emit_release_callable):
        self.layers = parsed_layout

        # actually more of a "which layers are enabled with what priority" maybe?
        # fails to model a layer which has a toggle for itself (e.g. you can get it it temporarily with a :to(...) then
        # toggle it permanently with a :toggle(...) then press that toggle again to turn it off
        # TODO: handle temp-to-toggle layers
        self.layer_stack = LayerStack()
        self.as_pressed = {}

        self.emit_press = emit_press_callable
        self.emit_release = emit_release_callable

    def lookup(self, x, y):
        # TODO: check this performs adequately in the normal case
        for layer_name in self.layer_stack.enabled_layers:
            prospective = self.layers[layer_name][y][x]
            if prospective[0] != 't':
                return prospective

    def press(self, x, y):
        action = self.lookup(x, y)
        self.as_pressed[x, y] = action

        command, values = action

        if command in LAYER_COMMANDS:
            getattr(self, 'handle_{}_pressed'.format(command))(values)
        else:
            self.emit_press(action)

    def release(self, x, y):
        action = self.as_pressed.pop((x, y))
        command, values = action

        if command in LAYER_COMMANDS:
            getattr(self, 'handle_{}_released'.format(command))(values)
        else:
            self.emit_release(action)

    def handle_to_pressed(self, args):
        layer = args[0]
        self.layer_stack.to(layer)

    def handle_to_released(self, args):
        layer = args[0]
        self.layer_stack.un_to(layer)

    def handle_toggle_pressed(self, args):
        pass  # we ignore the press and only react upon release

    def handle_toggle_released(self, args):
        layer = args[0]
        self.layer_stack.toggle(layer)
