import colorama
from time import time, sleep
from contextlib import suppress

from terribleconsolegui import Layout, GUIElement, GUICounter, print_pos, PopGUISection


colorama.init()


class TypeSelection(Layout):
    def __init__(self, line: int):
        super().__init__(GUIElement('Timer', 3, line, selected=True),
                         GUIElement('Stop Watch', 10, line),
                         exclusive=True)
        self.keys = {
            'left':  self.previous,
            'right': self.next,
            'a':     self.previous,
            'd':     self.next,
            'esc':   exit,
            'enter': None,
        }


class TimeSelection(Layout):
    def __init__(self, line: int):
        self.line = line
        super().__init__(GUICounter(3, self.line, align='right', padding=2, bounds=(0, 23)),
                         GUICounter(6, self.line, align='right', padding=2, bounds=(0, 59)),
                         GUICounter(9, self.line, align='right', padding=2, bounds=(0, 59)),
                         starting_index=2, exclusive=True)
        self.keys = {
            'left':  self.previous,
            'right': self.next,
            'a':     self.previous,
            'd':     self.next,
            'up':    lambda: self.current.increase(),
            'down':  lambda: self.current.decrease(),
            'w':     lambda: self.current.increase(),
            's':     lambda: self.current.decrease(),
            'esc':   exit,
            'back':  self.pop_section,
            'enter': None,
        }
    
    def init(self):
        #          hh:mm:ss
        print_pos('  :  :  ', 3, self.line)
    
    def result(self):
        self.deselect_all()
        return self[2].count + self[1].count * 60 + self[0].count * 60 ** 2
    
    def cleanup(self):
        print_pos('        ', 2, self.line)
    
    def pop_section(self):
        self.clear_all()
        raise PopGUISection()


def main():
    while True:
        type_ = TypeSelection(line=2).run_loop().text
        with suppress(PopGUISection):
            total = TimeSelection(line=4).run_loop()
            break
    print_pos(f'Thats {total} seconds, with a {type_}', 1, 6)
    # Implementing the actual timer is left as an exercise for the reader (or until I feel like doing it).


if __name__ == '__main__':
    main()
    input()
