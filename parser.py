from argparse import ArgumentParser
from rich.text import Text

from constants import APPLY_TO_OPTIONS
from ui import console, theme, banner


class CustomParser(ArgumentParser):
    """Custom argument parser."""

    def print_help(self, file=None):
        console.print(Text(banner, style=theme.primary + " bold"))
        return super().print_help(file)


def get_argparser(
    directory: str, pattern: str, replacement: str, options: dict
) -> CustomParser:
    """Parse and return the command-line arguments."""
    parser = CustomParser(
        description="A command-line tool for bulk file renaming and organization using regex.",
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=directory,
        help=f"Directory where files are located (default is {directory}).",
    )
    parser.add_argument(
        "pattern",
        nargs="?",
        default=pattern,
        help=f"Search pattern for renaming (default is {pattern}).",
    )
    parser.add_argument(
        "replacement",
        nargs="?",
        default=replacement,
        help=f"Replacement string for the pattern (default is {replacement}).",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=options["count"],
        help=f"Max replacements per file (default is {options['count']}).",
    )
    parser.add_argument(
        "-r",
        "--regex",
        action="store_true",
        default=options["regex"],
        help=f"Treats the pattern as a regular expression (default is {options['regex']}).",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        default=options["case_sensitive"],
        help=f"Make the search case-sensitive (default is {options['case_sensitive']}).",
    )
    parser.add_argument(
        "--apply-to",
        choices=[option[1] for option in APPLY_TO_OPTIONS],
        default=options["apply_to"],
        help=f"Specifies where the renaming should be applied (default is {options['apply_to']}).",
    )

    return parser
