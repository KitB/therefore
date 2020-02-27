from therefore.writekeys import Output, Layout
from therefore import usb, readkeys

layout_definition = [
    ['`', '1', '2', '3', '4', '5', 'fn'],
    ['tab', 'q', 'w', 'e', 'r', 't', ' '],
    ['caps_lock', 'a', 's', 'd', 'f', 'g', ' '],
    ['shift', 'z', 'x', 'c', 'v', 'b', ' '],
    ['control', 'win', 'alt', ' ', ' ', ' ', ' '],
    ['backspace', ' ', 'windows'],
]


def reverse(l):
    return list(reversed(l))


layout_definition = reverse([reverse(row) for row in layout_definition])

output = Output(
    layout=Layout(layout_definition),
    keyboard=usb.keyboard,
)

if __name__ == '__main__':
    previous = set()
    while True:
        current = set(readkeys.get_pressed_keys())
        new = current - previous
        gone = previous - current

        output.press(*new)
        output.release(*gone)

        previous = current
