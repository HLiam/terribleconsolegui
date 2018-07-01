from .guielements import GUIElement
from .keyloop import callbacks, CallbackNode
from contextlib import suppress


class GUILayout:
    def __init__(self, *args: GUIElement, starting_index: int=0, wrap: bool=True,
                 exclusive: bool=False):
        if not isinstance(args[0], GUIElement):
            args = args[0]
        self.elements = list(args)
        self.wrap = wrap
        self._current_index = starting_index
        if exclusive:
            for element in self.elements:
                element.exclusive_to = args

    def __repr__(self):
        return 'Layout(current={current!r}, wrap={wrap!r}, [{elements}])'.format(
            current=self.current, wrap=self.wrap,
            elements=', '.join([repr(elements) for elements in self.elements]))

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
    def current(self) -> GUIElement:
        """The currently focused element.

        When set, the element it's set to will become focused.
        """
        return self.elements[self._current_index]

    @current.setter
    def current(self, element):
        self._current_index = self.elements.index(element)
        element.select()

    def init(self):
        """Draw any gui prerequisites on the screen. User defined.

        This method is called before the `Layout.start()` loop runs.
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

    def result(self) -> GUIElement:
        return self.current  # idk if this is needed

    def previous(self):
        """Select the item to the left of the current item."""
        self._current_index = (self._current_index - 1) % len(self.elements)

    def next(self):
        """Select the item to the left of the current item."""
        self._current_index = (self._current_index + 1) % len(self.elements)
        current = self.current
        current.select()  # TODO fix this

    def bind_key(self, key: str, callback: object, auto_unbind: bool=False):
        """Bind `callback` funtion to `key`.

        Only one funtion can be bound to key at a time (per layout
        object).

        Args:
            key(str): The key to bind. The valid names are listed above.
                (TODO)
            callback(callable): The funtion (or callable) that will be
                called when the key is pressed.
            auto_unbind(bool, optional): Automatically unbind the key if
                it's already bound. Defaults to False.

        Raises:
            KeyError: If the key is already bound and `auto_unbind` is
                False.
        """
        list_for_key = callbacks[key]
        if auto_unbind:
            self.unbind_key(key)
        elif [cbnode for cbnode in list_for_key if cbnode.bound is self]:
            raise KeyError(f'key {key!r} is invalid')
        list_for_key.append(CallbackNode(self, callback))

    def unbind_key(self, key: str):
        with suppress(IndexError):
            callbacks[key] = [cbnode for cbnode in callbacks[key] if cbnode.bound is not self]
