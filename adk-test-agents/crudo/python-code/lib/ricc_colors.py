# lib/ricc_colors.py
# Simple ANSI color codes for fun terminal output! ✨

COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_MAGENTA = "\033[95m"
COLOR_CYAN = "\033[96m"
COLOR_ORANGE = "\033[38;5;208m"
COLOR_BOLD = "\033[1m"
COLOR_DARKGRAY = "\033[90m"

def red(text: str) -> str:
    """Makes text red"""
    return f"{COLOR_RED}{text}{COLOR_RESET}"

def green(text: str) -> str:
    """Makes text green"""
    return f"{COLOR_GREEN}{text}{COLOR_RESET}"

def yellow(text: str) -> str:
    """Makes text yellow"""
    return f"{COLOR_YELLOW}{text}{COLOR_RESET}"

def blue(text: str) -> str:
    """Makes text blue"""
    return f"{COLOR_BLUE}{text}{COLOR_RESET}"

def magenta(text: str) -> str:
    """Makes text magenta"""
    return f"{COLOR_MAGENTA}{text}{COLOR_RESET}"

def cyan(text: str) -> str:
    """Makes text cyan"""
    return f"{COLOR_CYAN}{text}{COLOR_RESET}"

def darkgray(text: str) -> str:
    """Makes text cyan"""
    return f"{COLOR_DARKGRAY}{text}{COLOR_RESET}"

def orange(text: str) -> str:
    """Makes text orange"""
    return f"{COLOR_ORANGE}{text}{COLOR_RESET}"

def bold(text: str) -> str:
    """Makes text bold"""
    return f"{COLOR_BOLD}{text}{COLOR_RESET}"

def purple(text: str) -> str:
    """Makes text purple"""
    return f"{COLOR_MAGENTA}{text}{COLOR_RESET}"

def underline(text: str) -> str:
    """Makes text underline"""
    return f"\033[4m{text}\033[0m"

def italic(text: str) -> str:
    """Makes text italic"""
    return f"\033[3m{text}\033[0m"



# --- Emojis ---
USER_ICON = "🧑"
TOOL_ICON = "⚒️"
GEMINI_ICON = "♊"
INFO_ICON = "ℹ️"
WARN_ICON = "⚠️"
ERROR_ICON = "🚨"
CACHE_ICON = "💾"
CLOUD_ICON = "☁️"
FUN_CALL = TOOL_ICON



