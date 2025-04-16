class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @staticmethod
    def red(text: str) -> str: return f"{Color.RED}{text}{Color.END}"
    def green(text: str) -> str: return f"{Color.GREEN}{text}{Color.END}"
    def yellow(text: str) -> str: return f"{Color.YELLOW}{text}{Color.END}"
    def blue(text: str) -> str: return f"{Color.BLUE}{text}{Color.END}"

    # ... other colors ...
    @staticmethod
    def bold(text: str) -> str: return f"{Color.BOLD}{text}{Color.END}"
