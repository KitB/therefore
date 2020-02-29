from adafruit_hid.keycode import Keycode

DEFAULT_KEYCODE = Keycode.SPACE

lookups = {
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
    '\\': 'backslash',
    '=': 'equals',
    '-': 'minus',
    'ins': 'insert',
    'del': 'delete',
    'win': 'gui',
    'left': 'left_arrow',
    'right': 'right_arrow',
    'up': 'up_arrow',
    'down': 'down_arrow',
    'caps': 'caps_lock',
    '(': ['shift', 'nine'],
    ')': ['shift', 'zero'],
    '_': ['shift', '-'],
}

def lookup_keystr(keystr, default=DEFAULT_KEYCODE):
    keystr = lookups.get(keystr, keystr)
    try:
        return getattr(Keycode, keystr.upper())
    except AttributeError:
        if keystr in syscodes:
            return keystr
        return default


def parse_syskey(keystr):
    keystr = keystr.replace(')', '')
    command, _, argstr = keystr[1:].partition('(')
    args = argstr.split(',')
    return (command, args)

def parse(keystr):
    # check for defined aliases
    keystr = lookups.get(keystr, keystr)

    # check for compound keys
    if isinstance(keystr, list):
        return [parse(k) for k in keystr]

    # check for system keys
    if keystr[0] == ':':
        return parse_syskey(keystr)

    # try for a key code
    try:
        return getattr(Keycode, keystr.upper())
    except AttributeError:
        return DEFAULT_KEYCODE


class Layer:
    def __init__(self, definition):
        self.table = [[parse(keystr) for keystr in row] for row in definition]

    def __getitem__(self, loc):
        column, row = loc
        try:
            return self.table[row][column]
        except IndexError:
            return DEFAULT_KEYCODE


class Layout:
    """
    Converts (column, row) locations into actionable objects based on a given layout definition
    """
    def __init__(self, definition):
        self.layers = {name: Layer(value) for name, value in definition['layers'].items()}
        self.layer_stack = ['default']

    def __getitem__(self, loc):
        out = ('t',[''])
        stack_pos = -1
        while out == ('t',['']):
            out = self.layers[self.layer_stack[stack_pos]][loc]
            stack_pos -= 1
        return out

    def push(self, layer):
        self.layer_stack.append(layer)

    def pop(self):
        self.layer_stack.pop()


class SystemKeyPressed(Exception):
    def __init__(self, keycode):
        # TODO: don't use exceptions for normal control flow
        # this was just a quick and dirty hack
        self.keycode = keycode


class Output:
    def __init__(self, layout, keyboard):
        self.keyboard = keyboard
        self.layout = layout

        self.layer = 'default'

    def press(self, location):
        keycode = self.layout[location]
        try:
            self.keyboard.press(keycode)
        except TypeError:
            if isinstance(keycode, tuple):
                self.handle_system_press(*keycode)
            elif isinstance(keycode, list):
                self.keyboard.press(*keycode)

    def release(self, location):
        keycode = self.layout[location]
        try:
            self.keyboard.release(keycode)
        except TypeError:
            if isinstance(keycode, tuple):
                self.handle_system_release(*keycode)
            elif isinstance(keycode, list):
                self.keyboard.release(*keycode)

    def handle_system_press(self, command, args):
        if command == 'to':
            self.layout.push(args[0])
        else:
            raise SystemKeyPressed(command)

    def handle_system_release(self, command, args):
        if command == 'to':
            self.layout.pop()
