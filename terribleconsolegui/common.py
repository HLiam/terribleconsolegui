from colorama import Fore, Back


def print_pos(text: str, x: int, y: int, fore=Fore.RESET, back=Back.RESET):
    """Print a colored string at a specific x and y of the console."""
    if fore == Fore.RESET and back == Back.RESET:
        print(f'\033[{y};{x}H', end=str(text))
    else:
        print(f'\033[{y};{x}H', end=''.join((fore, back, str(text), Fore.RESET, Back.RESET)))
