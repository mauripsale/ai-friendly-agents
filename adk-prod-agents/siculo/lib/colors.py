# lib/colors.py
from typing import Optional # Add Optional
import html # Import html for escaping

class Color:
    # --- ANSI Codes (Keep these) ---
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

    # --- ANSI Methods (Keep these) ---
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

    # --- HTML/Markdown Mappings & Methods (NEW) ---
    # Using common web colors or brighter alternatives
    HTML_COLOR_MAP = {
        'RED': '#E57373',      # Material Design Red 300
        'GREEN': '#81C784',    # Material Design Green 300
        'YELLOW': '#FFF176',   # Material Design Yellow 300
        'BLUE': '#64B5F6',     # Material Design Blue 300
        'MAGENTA': '#F06292',  # Material Design Pink 300
        'CYAN': '#4DD0E1',     # Material Design Cyan 300
        'WHITE': '#F5F5F5',    # Grey 100 (off-white)
        'GREY': '#BDBDBD',     # Grey 400
    }

    @staticmethod
    def _html_span(text: str, color_name: Optional[str] = None, bold: bool = False) -> str:
        """Internal helper to create styled HTML spans."""
        # Escape HTML special characters in the text itself to prevent injection
        import html
        safe_text = html.escape(text)

        styles = []
        outer_tag = None

        if color_name and color_name in Color.HTML_COLOR_MAP:
            styles.append(f"color:{Color.HTML_COLOR_MAP[color_name]}")

        # Use <strong> for bold for better semantics in Markdown/HTML
        if bold:
            outer_tag = "strong"

        if styles:
            style_attr = ";".join(styles)
            content = f'<span style="{style_attr}">{safe_text}</span>'
            if outer_tag:
                return f"<{outer_tag}>{content}</{outer_tag}>"
            else:
                return content
        elif outer_tag: # Only bold requested
            return f"<{outer_tag}>{safe_text}</{outer_tag}>"
        else:
            return safe_text # No styling needed

    # --- Public HTML Methods ---
    @staticmethod
    def html_red(text: str) -> str: return Color._html_span(text, 'RED')
    @staticmethod
    def html_green(text: str) -> str: return Color._html_span(text, 'GREEN')
    @staticmethod
    def html_yellow(text: str) -> str: return Color._html_span(text, 'YELLOW')
    @staticmethod
    def html_blue(text: str) -> str: return Color._html_span(text, 'BLUE')
    @staticmethod
    def html_magenta(text: str) -> str: return Color._html_span(text, 'MAGENTA')
    @staticmethod
    def html_cyan(text: str) -> str: return Color._html_span(text, 'CYAN')
    @staticmethod
    def html_white(text: str) -> str: return Color._html_span(text, 'WHITE')
    @staticmethod
    def html_grey(text: str) -> str: return Color._html_span(text, 'GREY')

    @staticmethod
    def html_bold(text: str) -> str: return Color._html_span(text, bold=True)
    # We'll skip underline for Markdown as it's less standard / visually appealing
