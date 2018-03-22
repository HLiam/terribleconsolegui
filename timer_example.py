import colorama
from time import time, sleep
from contextlib import suppress

from terribleconsolegui import Layout, GUIElement, GUICounter, print_pos, PopGUISection


colorama.init()


def get_type(line):
    elements = Layout(GUIElement('Timer', 3, line, selected=True),
                      GUIElement('Stop Watch', 10, line),
                      exclusive=True)
    for key in elements.key_presses(auto_left_right=True, auto_esc=True, auto_enter=True):
        pass
    return elements.current.text


def get_time(line):
    #          hh:mm:ss
    elements = Layout(GUICounter(3, line, align='right', padding=2, bounds=(0, 23)),
                      GUICounter(6, line, align='right', padding=2, bounds=(0, 59)),
                      GUICounter(9, line, align='right', padding=2, bounds=(0, 59)),
                      default=2, exclusive=True)
    elements.init = lambda: print_pos('  :  :  ', 3, line)
    elements.cleanup = lambda: print_pos('        ', 2, line)
    for key in elements.key_presses(auto_left_right=True, auto_up_down=True, auto_esc=True, auto_enter=True):
        if key == 'back':
            elements.clear_all()
            raise PopGUISection()
    elements.deselect_all()
    return elements[2].count + elements[1].count * 60 + elements[0].count * 60 ** 2


def main():
    while True:
        type_ = get_type(line=2)
        with suppress(PopGUISection):
            total = get_time(line=4)
            break
    print_pos(f'Thats {total} seconds, with a {type_}', 1, 6)
    # Implementing the actual timer is left as an exercise for the reader (or until I feel like doing it).


if __name__ == '__main__':
    main()
    input()
