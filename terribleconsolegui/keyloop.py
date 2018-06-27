from threading import Thread
try:
    from msvcrt import getch
except ImportError as e:
    raise OSError('only works on windows')


keys = {
    b' ':        'space',
    b'\x1c':     '^\\',
    b'\x1b':     'esc',
    b'\r':       'enter',
    b'\n':       '^enter',
    b'\t':       'tab',
    b'\x95':     '^tab',
    b'\x08':     'back',
    b'\x7f':     '^back',
    b'\xe0S':    'del',
    b'\xe0\x93': '^del',
    b'\xe0G':    'home',
    b'\xe0w':    '^home',
    b'\xe0O':    'end',
    b'\xe0u':    '^end',
    b'\xe0I':    'pgup',
    b'\xe0Q':    'pgdn',
    b'\x00R':    'num0',
    b'\x00O':    'num1',
    b'\x00P':    'num2',
    b'\x00Q':    'num3',
    b'\x00K':    'num4',
    b'\x00M':    'num6',
    b'\x00G':    'num7',
    b'\x00H':    'num8',
    b'\x00I':    'num9',
    b'\x00S':    'num.',
    b'\x00\x92': '^num0',
    b'\x00u':    '^num1',
    b'\x00\x91': '^num2',
    b'\x00v':    '^num3',
    b'\x00s':    '^num4',
    b'\x00t':    '^num6',
    b'\x00w':    '^num7',
    b'\x00\x8d': '^num8',
    b'\x00\x84': '^num9',
    b'\x00\x93': '^num.',
    b'\x00\x95': '^num/',
    b'\x00;':    'f1',
    b'\x00<':    'f2',
    b'\x00=':    'f3',
    b'\x00>':    'f4',
    b'\x00?':    'f5',
    b'\x00@':    'f6',
    b'\x00A':    'f7',
    b'\x00B':    'f8',
    b'\x00C':    'f9',
    b'\x00D':    'f10',
    b'\xe0\x85': 'f11',
    b'\xe0\x86': 'f12',
    b'\xe0H':    'up',
    b'\xe0P':    'down',
    b'\xe0K':    'left',
    b'\xe0M':    'right',
}
keys.update({bytes((i,)): chr(i) for i in range(32, 127)})
# _keys.update({bytes((i,)): f'^{chr(i + 65)}' for i in range(0, 26)})  # ctrl+char
callbacks = {key: [] for key in keys.values()}  # maybe make the values sets instead of lists
callbacks['default'] = []


class CallbackNode:
    __slots__ = ('bound', 'callback')

    def __init__(self, bound: object, callback: object):
        self.bound = bound
        self.callback = callback


def listen_for_key() -> str:
    """Return the friendly name of the next pressed key (blocking)."""
    key = getch()
    if key == b'\x00' or key == b'\xe0':
        key += getch()
    return keys[key]


def _start_keypress_loop(self):
    while True:
        key = listen_for_key()
        key_callbacks = callbacks[key]
        if key_callbacks:
            for cbnode in key_callbacks:
                cbnode.callback.__call__()
        else:
            for cbnode in callbacks['default']:
                cbnode.callback.__call__(key)

def start_keypress_loop():
    Thread(target=_start_keypress_loop).start()
