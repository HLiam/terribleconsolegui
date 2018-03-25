from colorama import Fore, Back


def print_pos(text: str, x: int, y: int, fore=Fore.RESET, back=Back.RESET):
    """Print a colored string at a specific x and y of the console."""
    print(f'\033[{y};{x}H', end=''.join((fore, back, str(text), Fore.RESET, Back.RESET)))
