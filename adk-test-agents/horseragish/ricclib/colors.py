# ricclib/colors.py
from typing import Dict

class AnsiColors:
    """A simple class to add ANSI colors to terminal output. 🌈"""
    COLORS: Dict[str, str] = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "orange": "\033[38;5;208m", # A nice, zesty orange
        "purple": "\033[38;5;93m",  # A regal purple
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    }

    @staticmethod
    def colorize(text: str, color_name: str) -> str:
        """Colorizes the given text with the specified ANSI color."""
        color_code = AnsiColors.COLORS.get(color_name.lower())
        if color_code:
            return f"{color_code}{text}{AnsiColors.COLORS['reset']}"
        return text

    # Adding the 10 most typical colors as methods for convenience
    @staticmethod
    def red(text: str) -> str: return AnsiColors.colorize(text, "red")
    @staticmethod
    def green(text: str) -> str: return AnsiColors.colorize(text, "green")
    @staticmethod
    def yellow(text: str) -> str: return AnsiColors.colorize(text, "yellow")
    @staticmethod
    def blue(text: str) -> str: return AnsiColors.colorize(text, "blue")
    @staticmethod
    def magenta(text: str) -> str: return AnsiColors.colorize(text, "magenta")
    @staticmethod
    def cyan(text: str) -> str: return AnsiColors.colorize(text, "cyan")
    @staticmethod
    def white(text: str) -> str: return AnsiColors.colorize(text, "white")
    @staticmethod
    def black(text: str) -> str: return AnsiColors.colorize(text, "black")
    @staticmethod
    def orange(text: str) -> str: return AnsiColors.colorize(text, "orange")
    @staticmethod
    def purple(text: str) -> str: return AnsiColors.colorize(text, "purple")

    @staticmethod
    def bold(text: str) -> str: return AnsiColors.colorize(text, "bold")
    @staticmethod
    def underline(text: str) -> str: return AnsiColors.colorize(text, "underline")

if __name__ == "__main__":
    print(AnsiColors.red("This is red! Success! 🔥"))
    print(AnsiColors.green(f"{AnsiColors.bold('This is green and bold!')} Success! 🌿"))
    print(AnsiColors.underline(AnsiColors.blue("This is blue and underlined.")) + " Success! 💧")
    print(AnsiColors.orange("This is orange, how a-peeling! 🍊"))
    print(AnsiColors.purple("Feeling royal in purple! 👑"))
    print(AnsiColors.cyan("Cyan-tifically proven to be cool! 🧪"))
    print(AnsiColors.magenta("Magenta-nificent! 💖"))
    print(AnsiColors.white("White as freshly fallen snow. ❄️"))
    print(AnsiColors.black("Black, the new... well, it's always been cool. 🖤"))
