# lib/colors.py
class Color:
    """A simple class for adding ANSI color codes to text."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GREY = '\033[90m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m' # Resets all attributes

    @staticmethod
    def red(text: str) -> str: return f"{Color.RED}{text}{Color.END}"
    @staticmethod
    def green(text: str) -> str: return f"{Color.GREEN}{text}{Color.END}"
    @staticmethod
    def yellow(text: str) -> str: return f"{Color.YELLOW}{text}{Color.END}"
    @staticmethod
    def blue(text: str) -> str: return f"{Color.BLUE}{text}{Color.END}"
    @staticmethod
    def magenta(text: str) -> str: return f"{Color.MAGENTA}{text}{Color.END}"
    @staticmethod
    def cyan(text: str) -> str: return f"{Color.CYAN}{text}{Color.END}"
    @staticmethod
    def white(text: str) -> str: return f"{Color.WHITE}{text}{Color.END}"
    @staticmethod
    def grey(text: str) -> str: return f"{Color.GREY}{text}{Color.END}"
    @staticmethod
    def bold(text: str) -> str: return f"{Color.BOLD}{text}{Color.END}"
    @staticmethod
    def underline(text: str) -> str: return f"{Color.UNDERLINE}{text}{Color.END}"
