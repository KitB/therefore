"""

Codes:
Special keys start with ':'

:t        transparent (get key from previous layer)
:_        no key here -- so this should never be accessed
:switch   switch between BLE and USB modes
:reset    reset the keyboard
:to(...)  go to layer '...' while button is held

"""
fn = ':to(functions)'
layout = {
    'layers': {
        'default': [
            ['`'    , '1', '2', '3', '4', '5', 'del'  ,   ':switch' , '6', '7', '8', '9', '0', '-'          ],
            ['tab'  , 'q', 'w', 'e', 'r', 't', '\\'   ,   '['      , 'y', 'u', 'i', 'o', 'p', '='          ],
            ['caps' , 'a', 's', 'd', 'f', 'g',  fn    ,   ']'      , 'h', 'j', 'k', 'l', ';', '\''         ],
            ['shift', 'z', 'x', 'c', 'v', 'b', 'ins'  ,   'page_up', 'n', 'm', ',', '.', '/', 'right_shift'],

            ['control', ' ', ' ', 'win', 'alt', 'home', 'end', 'page_down', 'right_alt', 'left', 'down', 'up', 'right', 'right_control'],
            [':_', ':_', ':_', ':_', 'backspace', ':to(left thumb)', 'win', 'win', 'enter', 'spacebar', ':_', ':_', ':_', ':_'],
        ],
        'left thumb': [
            # `     1     2     3     4     5     d     s     6     7     8     9     0     -
            [':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', '^' , '&' , '*' , ':t', ':t', ':t'],
            [':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t'],
            [':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', '(' , ')' , '#' , '~' , ':t'],
            [':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t'],

            [':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t'],
            [':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t'],
        ],
        'functions': [
            # `     1     2     3     4     5     d     s     6     7     8     9     0     -
            ['f11','f1', 'f2', 'f3', 'f4', 'f5', ':t', ':t', 'f6', 'f7', 'f8', 'f9', 'f10','f12'],
            [':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t'],
            [':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t'],
            [':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t'],

            [':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t'],
            [':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t', ':t'],
        ],
    },
}
