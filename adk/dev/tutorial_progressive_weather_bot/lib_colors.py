import sys

def yellow(str):
    """Formats the input string with yellow color using ANSI escape codes."""
    return f"\033[93m{str}\033[0m"

def red(str):
    """Formats the input string with red color using ANSI escape codes."""
    return f"\033[91m{str}\033[0m"

def green(str):
    """Formats the input string with green color using ANSI escape codes."""
    return f"\033[92m{str}\033[0m"

def blue(str):
    """Formats the input string with blue color using ANSI escape codes."""
    return f"\033[94m{str}\033[0m"

def magenta(str):
    """Formats the input string with magenta color using ANSI escape codes."""
    return f"\033[95m{str}\033[0m"

def cyan(str):
    """Formats the input string with cyan color using ANSI escape codes."""
    return f"\033[96m{str}\033[0m"

def gray(str):
    """Formats the input string with bright gray color using ANSI escape codes."""
    return f"\033[90m{str}\033[0m"

def bold(str):
    """Formats the input string with bold color using ANSI escape codes."""
    return f"\033[1m{str}\033[0m"

def underline(str):
    """Formats the input string with underline color using ANSI escape codes."""
    return f"\033[4m{str}\033[0m"

def italic(str):
    """Formats the input string with italic color using ANSI escape codes."""
    return f"\033[3m{str}\033[0m"

def blink(str):
    """Formats the input string with blink color using ANSI escape codes."""
    return f"\033[5m{str}\033[0m"

def reverse(str):
    """Formats the input string with reverse color using ANSI escape codes."""
    return f"\033[7m{str}\033[0m"

# def black(s):
#     return magenta(s)
# def blue(s):
#     return magenta(s)

def purple(s):
    '''synonim'''
    return magenta(s)

def white(text: str) -> str:
    """Formats the input string with bold bright white color using ANSI escape codes."""
    # Check if the output stream supports ANSI escape codes
    # \033[1m is the code for bold
    # \033[97m is the code for bright white
    # \033[0m resets all formatting
    if sys.stdout.isatty():
        return f"\033[1m\033[97m{text}\033[0m"
    return text
