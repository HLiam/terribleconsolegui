from colorama import Fore, Back


FRESET = Fore.RESET
BRESET = Back.RESET


def print_pos(text: str, x: int, y: int, fore=Fore.RESET, back=Back.RESET):
    """Print a colored string at a specific x and y of the console."""
    if fore == FRESET and back == BRESET:
        print(f'\033[{y};{x}H', end=str(text))
    else:
        print(f'\033[{y};{x}H', end=''.join((fore, back, str(text), FRESET, BRESET)))
