from math import inf
from colorama import Fore, Back

from .common import print_pos


class PopGUISection(Exception):
    """This exception should be raised when closing and cleaning up a
    gui section.
    """
    pass


class GUIElement:
    """The base GUI element. All other GUI elements inherit from this.
    
    Args:
        text(str): The text to display.
        x(int): The x (col) of the terminal to display at.
        y(int): The y (row) of the terminal to display at.
        sel_fore(str, optional): The color of the foreground when
            selected. Should be an ANSI color code. Defaults to
            `Fore.RESET`.
        sel_back(str, optional): The color of the background when
            selected. Should be an ANSI color code. Defaults to
            `Back.GREEN`.
        unsel_fore(str, optional): The color of the foreground when
            unselected. Should be an ANSI color code. Defaults to
            `Fore.RESET`.
        unsel_back(str, optional): The color of the background when
            unselected. Should be an ANSI color code. Defaults to
            `Back.RESET`.
        selected(bool, optional): Whether or not this element should be
            selected by default. Defaults to False.
    
    Attributes:
        text(str): The text to display.
        x(int): The x (col) of the terminal to display at.
        y(int): The y (row) of the terminal to display at.
        sel_fore(str): The color of the foreground when selected.
        sel_back(str): The color of the background when selected.
        unsel_fore(str): The color of the foreground when unselected.
        unsel_back(str): The color of the background when unselected.
        selected(bool): Whether or not this element is selected.
        exclusive_to(list): A list of other gui elements that are
            mutually exclusive to this element. If this element is
            selected is selected, all the elements in this list will be
            deselected. If the list contains this element, it will be
            skipped.
    
    TODO:
        Rewrite to remove selectability, then add a new `GUISelectable`
            that contains two `GUIElement`s, one called `selected` and
            the other called `unselected`.
    """
    
    def __init__(self, text, x, y, sel_fore=Fore.RESET, sel_back=Back.GREEN,
                 unsel_fore=Fore.RESET, unsel_back=Back.RESET, selected=False):
        self.text = text
        self.x = x
        self.y = y
        self.selected = selected
        self.sel_fore = sel_fore
        self.sel_back = sel_back
        self.unsel_fore = unsel_fore
        self.unsel_back = unsel_back
        self.exclusive_to = []
    
    def set_color(self, sel_fore=None, sel_back=None, unsel_fore=None, unsel_back=None):
        """Change the selected/unselected foreground/background color.
        
        Args:
            sel_fore(str, optional): The selected foreground color.
            sel_back(str, optional): The selected background color.
            unsel_fore(str, optional): The unselected foreground color.
            unsel_back(str, optional): The unselected background color.
        """
        if sel_fore is not None:
            self.sel_fore = sel_fore
        if sel_back is not None:
            self.sel_back = sel_back
        if unsel_fore is not None:
            self.unsel_fore = unsel_fore
        if unsel_back is not None:
            self.unsel_back = unsel_back
        self.update()
    
    def update(self, text: str=None):
        """Update the text and color of the gui element.
        
        Args:
            text(str, optional): If passed, set the text to this before
                updating.
        """
        if text is None:
            text = self.text
        fore = self.sel_fore if self.selected else self.unsel_fore
        back = self.sel_back if self.selected else self.unsel_back
        print_pos(text, self.x, self.y, fore, back)
    
    def select(self):
        """Select this gui element.
        
        Change the colors to the selected colors. Any gui elements in
        this objects `exclusive_to` attribute will be deselected.
        """
        for element in self.exclusive_to:
            if element.selected and element is not self:
                element.deselect()
        self.selected = True
        self.update()
    
    def deselect(self):
        """Deselected this element."""
        self.selected = False
        self.update()
    
    def clear(self, length=None):
        """Clear the displayed text and coloring.
        
        After the text is cleared, this element's `cleanup` method is
        called. The `cleanup` method should be overwritten to write over
        anything associated with this gui element that would otherwise
        not be overwritten.
        
        Args:
            length(int, optional): If passed, this many columns will be
            overwritten. Defaults to the length of this objects `text`
            attribute.
        """
        self.deselect()
        if length is None:
            length = len(str(self.text))
        print_pos(' ' * length, self.x, self.y, Fore.RESET, Back.RESET)
        self.cleanup()
    
    def cleanup(self):
        """Do additional cleanup as set by the user.
        
        This method should be overwritten to write over anything
        associated with this gui element that would otherwise not be
        overwritten.
        """
        pass


class GUICounter(GUIElement):
    def __init__(self, x, y, sel_fore=Fore.RESET, sel_back=Back.GREEN,
                 unsel_fore=Fore.RESET, unsel_back=Back.RESET,
                 selected=False, default=0, default_aux=0, align='left', padding=0,
                 bounds=(-inf, inf), aux_bounds=(-inf, inf), wrap_bounds=True):
        super().__init__(default, x, y, Fore.RESET, Back.GREEN, Fore.RESET, Back.RESET)
        self.count = default
        self.aux_count = default_aux
        self.align = align
        self.padding = padding
        self.bounds = bounds
        self.aux_bounds = aux_bounds
        self.wrap_bounds = wrap_bounds
    
    def update(self):
        if self.align == 'left':
            super().update(f'{self.count}')
        elif self.align == 'right':
            super().update(str(self.count).zfill(self.padding))
        else:
            raise ValueError("`GUICounter.align` must be either 'left' or 'right'")
    
    def clear(self, length=0):
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
