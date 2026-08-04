from importlib.resources import files

from rich.console import Console

# Path to the CSS file
CSS_PATH = files("renux.assets").joinpath("styles.tcss")

# Rich console
CONSOLE = Console()
