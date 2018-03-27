from .guielements import GUIElement
try:
    from msvcrt import getch
except ImportError:
    print('Only works on windows')


_keys = {
    b' ':        ' ',
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
    b'\xe0\x86': '^pgup',
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
    b'\xe0H':    'up',
    b'\xe0P':    'down',
    b'\xe0K':    'left',
    b'\xe0M':    'right',
}
_keys.update({bytes((i,)): chr(i) for i in range(32, 127)})
# _keys.update({bytes((i,)): f'^{chr(i + 65)}' for i in range(0, 26)})  # ctrl+char


# class _keyDecorator:
#     def __init__(self, layout):
#         self.layout = layout
    
#     def __call__(self, key):
#         def decorator(func):
#             @wraps(func)
#             def wrapped(*args, **kwargs):
#                 return func(*args, **kwargs)
#             return wrapped
#         return decorator


class _StopKeypressLoop(Exception):
    pass


class Layout:
    def __init__(self, *args, starting_index=0, wrap=True, exclusive=False, keys=None):
        if not isinstance(args[0], GUIElement):
            args = args[0]
        self.elements = list(args)
        self.wrap = wrap
        self._current_index = starting_index
        self._keys = keys if keys is not None else {}
        self.keys = self._keys
        self._running = False
        # self.key = _keyDecorator(self)
        if exclusive:
            for element in self.elements:
                element.exclusive_to = args
    
    def __repr__(self):
        return 'Layout(current={current!r}, wrap={wrap!r}, [{elements}])'.format(
            current=self.current, wrap=self.wrap, elements=', '.join([repr(elements) for elements in self.elements]))
    
    def __len__(self):
        return len(self.elements)
    
    def __iter__(self):
        return iter(self.elements)
    
    def __getitem__(self, index):
        return self.elements[index]
    
    def __setitem__(self, index, value):
        self.elements[index] = value
        self.elements[index].update()
    
    def __delitem__(self, index):
        self.elements[index].clear()
        del self.elements[index]
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.clear()
    
    @property
    def keys(self):
        return self._keys
    
    @keys.setter
    def keys(self, keys):
        if 'default' not in keys:
            keys['default'] = bool
        self._keys = keys
    
    @property
    def current(self):
        """The currently selected item.
        
        When set, the element it's set to will become selected.
        """
        return self.elements[self._current_index]
    
    @current.setter
    def current(self, element):
        self._current_index = self.elements.index(element)
        element.select()
    
    def init(self):
        """Draw any gui prerequisites on the screen. User defined.
        
        This method is called before the `Layout.key_presses()`
        loop runs.
        """
        pass
    
    def cleanup(self):
        """Do additional cleanup as set by the user.
        
        This method should be overwritten to write over anything
        associated with the gui elements that would otherwise not be
        overwritten.
        """
        pass
    
    def clear(self):
        """Clear every element.
        
        After every element is cleared (user defined `element.cleanup`
        is called on every element after clearing it), the
        `Layout.cleanup` method is called.
        """
        for element in self.elements:
            element.clear()
        self.cleanup()
    
    def deselect_all(self):
        """Deselect every element."""
        for element in self.elements:
            if element.selected:
                element.deselect()
    
    def exit(self):
        pass
    
    def result(self):
        return self.current
    
    def previous(self):
        """Select the item to the left of the current item."""
        self._current_index = (self._current_index - 1) % len(self.elements)
    
    def next(self):
        """Select the item to the left of the current item."""
        self._current_index = (self._current_index + 1) % len(self.elements)
        current = self.current
        if isinstance(current, Layout):
            self.stop()
            current.start()
        else:
            current.select()
    
    def stop(self):
        raise _StopKeypressLoop
    
    def start(self):
        try:
            self.running = True
            self.init()
            self.current.select()
            for element in self.elements:
                element.update()
            while True:
                key = getch()
                if key == b'\x00' or key == b'\xe0':
                    key += getch()
                key_friendly = _keys[key]
                try:
                    mapped_func = self._keys[key_friendly]
                    try:
                        mapped_func.__call__()
                    except AttributeError:
                        if mapped_func is None:
                            self.exit()
                            self.running = False
                            return self.result()
                        raise
                except KeyError:
                    self._keys['default'].__call__(key_friendly)
        except _StopKeypressLoop:
            self._running = False
            self.exit()
