from math import inf
from colorama import Fore, Back

from common import print_pos


class GUIElement:
    """The base GUI element. All other GUI elements inherit from this.
    
    Args:
        text(str): The text to display.
        x(int): The x (col) of the terminal to display at.
        y(int): The y (row) of the terminal to display at.
        has_focus(bool, optional): Whether or not this element should
            have foucs by default. Defaults to False.
    
    Attributes:
        x(int): The x (col) of the terminal to display at.
        y(int): The y (row) of the terminal to display at.
        has_focus(bool): Whether or not this element should have focus.
        exclusive_to(list): A list of other gui elements that are
            mutually exclusive to this element. If this element is
            selected is selected, all the elements in this list will be
            deselected. If the list contains this element, it will be
            skipped.
        TODO:
            Separate the fouc stuff into a different element so that
            the focused GUIElement doesn't have it's own focus stuff.
    """
    
    def __init__(self, x: int, y: int, fore=Fore.RESET, back=Back.RESET):
        self.x = x
        self.y = y
        self.fore = fore
        self.back = back
    
    def set_color(self, fore=None, back=None):
        """Change the selected/unselected foreground/background color.
        
        Args:
            fore(str, optional): The foreground color.
            back(str, optional): The background color.
        """
        if fore is not None:
            self.fore = fore
        if back is not None:
            self.back = back
        self.update()
    
    def update(self):
        """Update the element. This method should be overridden in
        children.
        """
        pass
    
    def clear(self):
        """Clear the displayed text and coloring.
        
        After the text is cleared, this element's `cleanup` method is
        called. The `cleanup` method should be overwritten to write over
        anything associated with this gui element that would otherwise
        not be overwritten.
        """
        self.cleanup()
    
    def cleanup(self):
        """Do additional cleanup as set by the user.
        
        This method should be overwritten to write over anything
        associated with this gui element that would otherwise not be
        overwritten.
        """
        pass


class GUIFocusable(GUIElement):
    def __init__(self, x: int, y: int, fore=Fore.RESET, back=Back.RESET,
                 focused=None, has_focus: bool=False):
        super().__init__(x, y, fore, back)
        self.has_focus = has_focus
        if focused is None:
            self.focused = GUIElement(x, y)
        elif isinstance(focused, dict):
            self.focused = GUIElement(x, y)
            self.focused.__dict__.update(focused)
        # Attibutes that are overridden by this element gained focus
        # will be stored here. When the element loses focus, the items
        # in this dict will be copied to the element's __dict__.
        self._unfocused_state = {}
        self.exclusive_to = []  # TODO make sure this works
    
    def focus(self):
        """Select this gui element.
        
        Change the colors to the selected colors. Any gui elements in
        this objects `exclusive_to` attribute will be deselected.
        """
        for element in self.exclusive_to:
            if element.selected and element is not self:
                element.deselect()
        for attr, value in self.focused.__dict__.items():
            if attr in self.__dict__:
                self._unfocused_state[attr] = self.__dict__[attr]
                self.__dict__[attr] = value
        self.has_focus = True
        self.update()
    
    def defocus(self):
        """Deselected this element."""
        self.__dict__.update(self._unfocused_state)
        self._unfocused_state = {}
        self.has_focus = False
        self.update()
    
    def cleanup(self):
        super().cleanup()
        self.defocus()


class GUIElement2d(GUIFocusable):
    def __init__(self, x: int, y: int, x2: int, y2: int,
                 fore=Fore.RESET, Back=Back.RESET, focused=None,
                 has_focus: bool=False):
        super().__init__(self, x, y, fore, back, focused, has_focus)
        self.x2 = x2
        self.y2 = y2
    
    def update(self):
        for col in range(self.y, self.y2):
            print_pos(' ' * x2 - x1, self.x, col, self.fore, self.back)


class GUITextElement(GUIFocusable):
    def __init__(self, x: int, y: int, text='', fore=Fore.RESET, back=Back.RESET focused=None, has_focus=False):
        super().__init__(x, y, fore, back, focused, has_focus)
        self.text = text
    
    def update(self):
        print_pos(self.text, self.x, self.y, self.fore, self.back)

    def set_text(self, text, fore=None, back=None):
        self.text = text
        if fore is not None:
            self.fore = fore
        if back is not None:
            self.back = back
        self.update()
    
    def clear(self, length=None):
        """"""
        super().clear()
        if length is None:
            length = len(self.text)
        print_pos(' ' * length, self.x, self.y)


class GUICounter(GUITextElement):
    def __init__(self, x, y, fore=Fore.RESET, back=Back.GREEN,
                 focused=None, has_focus=False, default=0,
                 align='left', padding=0, bounds=(-inf, inf), wrap_bounds=True):
        super().__init__(x, y, default, fore, back)
        self.count = default
        self.aux_count = default_aux
        self.align = align
        self.padding = padding
        self.bounds = bounds
        self.aux_bounds = aux_bounds
        self.wrap_bounds = wrap_bounds
    
    def update(self):
        if self.align == 'left':
            self.set_text(self.count)
        elif self.align == 'right':
            self.set_text(str(self.count).zfill(self.padding))
        else:
            raise ValueError("`GUICounter.align` must be either 'left' or 'right'")
    
    def clear(self, length: int=0):
        """Clear the displayed text and coloring.
        
        After the text is cleared, this element's `cleanup` method is
        called. The `cleanup` method should be overwritten to write over
        anything associated with this element that would otherwise not
        be overwritten.
        
        Args:
            length(int, optional): If passed, this many columns will be
            overwritten if it is larger than the length of current text,
            otherwise the length of the current text will be
            overwritten."""
        super().clear(max((length, len(str(self.text)), self.padding)))
    
    def increase(self):
        """Increase the counter."""
        if not self.count == self.bounds[1]:
            self.count += 1
        elif self.wrap_bounds:
            self.count = self.bounds[0]
        self.update()
    
    def decrease(self):
        """Decrease the counter."""
        if not self.count == self.bounds[0]:
            self.count -= 1
        elif self.wrap_bounds:
            self.count = self.bounds[1]
        self.update()
    
    def aux_increase(self):
        """Increase the auxiliary counter."""
        if not self.count == self.aux_bounds[1]:
            self.aux_count += 1
        elif self.wrap_bounds:
            self.count = self.aux_bounds[0]
        self.update()
    
    def aux_decrease(self):
        """Decrease the auxiliary counter."""
        if not self.count == self.aux_bounds[0]:
            self.aux_count -= 1
        elif self.wrap_bounds:
            self.count = self.aux_bounds[1]
        self.update()


class GUIHiddenList(GUICounter):
    def __init__(self, items, x, y, sel_fore=Fore.RESET, sel_back=Back.GREEN,
                 unsel_fore=Fore.RESET, unsel_back=Back.RESET,
                 selected=False, max_width=None, wrap=False):
        super().__init__(items[0], x, y, Fore.RESET, Back.GREEN, Fore.RESET, Back.RESET)
        self.items = items
        self.wrap = wrap
        if max_width is None:
            self.max_width = max(len(i) for i in self.items)
        else:
            self.max_width = max_width
    
    @property
    def current(self):
        """The currently displayed item."""
        return self.items[self.count % len(self.items)]
    
    def update(self):
        """Update the displayed text to the currently selected item."""
        GUIElement.update(self, self.current)
    
    def clear(self):
        """Clear the displayed text and coloring."""
        super().clear(self.max_width)
    
    def increase(self):
        """Increase the current item index then update the text.
        
        If the index is already at the last item and wrap isn't on,
        don't increase the index, otherwise do.
        """
        if self.count == len(self.items) - 1:
            if self.wrap:
                self.count += 1
        else:
            self.count += 1
        self.update()
    
    def decrease(self):
        """Decrease the current item index then update the text.
        
        If the index is already at the first item and wrap isn't on,
        don't decrease the index, otherwise do.
        """
        if self.count == 0:
            if self.wrap:
                self.count -= 1
        else:
            self.count -= 1
        self.update()
