import os
from argparse import ArgumentParser, Namespace
from rich.text import Text

from renux.ui import CONSOLE, THEME, BANNER
from renux.constants import DEFAULT_OPTIONS, APPLY_TO_OPTIONS


class CustomParser(ArgumentParser):
    """Custom argument parser."""

    def print_help(self, file=None):
        CONSOLE.print(Text(BANNER, style=THEME.primary + " bold"))
        return super().print_help(file)


def parse_args() -> Namespace:
    """Parse and return the command-line arguments."""
    parser = CustomParser(
        description="A command-line tool for bulk file renaming and organization using regex.",
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=os.getcwd(),
        help=f"Directory where files are located (default is current directory).",
    )
    parser.add_argument(
        "pattern",
        nargs="?",
        default="",
        help=f"Search pattern for renaming (default is '').",
    )
    parser.add_argument(
        "replacement",
        nargs="?",
        default="",
        help=f"Replacement string for the pattern (default is '').",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=DEFAULT_OPTIONS["count"],
        help=f"Max replacements per file (default is {DEFAULT_OPTIONS['count']}).",
    )
    parser.add_argument(
        "-r",
        "--regex",
        action="store_true",
        default=DEFAULT_OPTIONS["regex"],
        help=f"Treats the pattern as a regular expression (default is {DEFAULT_OPTIONS['regex']}).",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        default=DEFAULT_OPTIONS["case_sensitive"],
        help=f"Make the search case-sensitive (default is {DEFAULT_OPTIONS['case_sensitive']}).",
    )
    parser.add_argument(
        "--apply-to",
        choices=[option[1] for option in APPLY_TO_OPTIONS],
        default=DEFAULT_OPTIONS["apply_to"],
        help=f"Specifies where the renaming should be applied (default is {DEFAULT_OPTIONS['apply_to']}).",
    )

    return parser.parse_args()
