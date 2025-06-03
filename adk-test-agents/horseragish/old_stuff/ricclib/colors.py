from typing import Final

class Color:
    """
    Simple ANSI color codes for terminal output.
    Because life's too short for monochrome logs! 😉
    """
    BLACK: Final[str] = "\033[30m"
    RED: Final[str] = "\033[31m"
    GREEN: Final[str] = "\033[32m"
    YELLOW: Final[str] = "\033[33m"
    BLUE: Final[str] = "\033[34m"
    MAGENTA: Final[str] = "\033[35m"
    CYAN: Final[str] = "\033[36m"
    WHITE: Final[str] = "\033[37m"
    GREY: Final[str] = "\033[90m" # Bright Black / Grey
    BRIGHT_RED: Final[str] = "\033[91m"
    BRIGHT_GREEN: Final[str] = "\033[92m" # Tenth color example

    # Formatting
    BOLD: Final[str] = "\033[1m"
    UNDERLINE: Final[str] = "\033[4m"
    
    # Reset
    END: Final[str] = "\033[0m"

    # Example usage:
    # print(f"{Color.GREEN}This is green text.{Color.END}")
    # print(f"{Color.BOLD}{Color.RED}This is bold red text.{Color.END}")

    @staticmethod
    def list_ten_typical() -> None:
        """Prints a list of 10 typical colors with examples."""
        print(f"{Color.BLACK}1. Black{Color.END}")
        print(f"{Color.RED}2. Red{Color.END}")
        print(f"{Color.GREEN}3. Green{Color.END}")
        print(f"{Color.YELLOW}4. Yellow{Color.END}")
        print(f"{Color.BLUE}5. Blue{Color.END}")
        print(f"{Color.MAGENTA}6. Magenta{Color.END}")
        print(f"{Color.CYAN}7. Cyan{Color.END}")
        print(f"{Color.WHITE}8. White (may depend on terminal theme){Color.END}")
        print(f"{Color.GREY}9. Grey{Color.END}")
        print(f"{Color.BRIGHT_RED}10. Bright Red{Color.END}")
        print(f"{Color.BOLD}Bold example{Color.END}")
        print(f"{Color.UNDERLINE}Underline example{Color.END}")

