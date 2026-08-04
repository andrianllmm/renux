import dataclasses
from importlib.resources import files

from rich.console import Console
from textual.theme import BUILTIN_THEMES

# Path to the CSS file
CSS_PATH = files("renux.assets").joinpath("styles.tcss")

# Custom Textual theme, based on the built-in "textual-dark" theme with a
# minimal set of overrides for a near-black, neutral grayscale palette
# (inspired by Vercel/shadcn-ui), keeping vibrant color reserved for
# semantic states (focus, selection, errors, warnings, success).
THEME = dataclasses.replace(
    BUILTIN_THEMES["textual-dark"],
    name="renux",
    primary="#e4e4e7",
    secondary="#52525b",
    accent="#e4e4e7",
    foreground="#fafafa",
    background="#0a0a0a",
    surface="#111113",
    panel="#18181b",
)

# Rich console
CONSOLE = Console()
