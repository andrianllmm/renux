from importlib.resources import files

from rich.console import Console
from textual.theme import Theme

# Path to the CSS file
CSS_PATH = files("renux.assets").joinpath("styles.tcss")

# Textual Theme
THEME = Theme(
    name="gruvbox",
    primary="#85A598",
    secondary="#A89A85",
    warning="#fabd2f",
    error="#fb4934",
    success="#b8bb26",
    accent="#fabd2f",
    foreground="#fbf1c7",
    background="#282828",
    surface="#3c3836",
    panel="#504945",
    dark=True,
    variables={
        "block-cursor-foreground": "#fbf1c7",
        "input-selection-background": "#689d6a40",
    },
)

# Rich console
CONSOLE = Console()
