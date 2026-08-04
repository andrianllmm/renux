import os
import sys
from types import SimpleNamespace

import typer
from typer import rich_utils
from typer._click.core import Context, HelpFormatter
from typer._click.exceptions import UsageError
from typer.core import TyperCommand
from typer.main import get_command

from renux.constants import APPLY_TO_OPTIONS, DEFAULT_OPTIONS
from renux.tags_reference import render_text

TAGS_HELP = f"""
{render_text()}

See https://github.com/andrianllmm/renux#tags for full details.
"""

APPLY_TO_CHOICES = [option[1] for option in APPLY_TO_OPTIONS]


class TagsHelpCommand(TyperCommand):
    """Renders the tags reference as its own panel, matching the style
    rich-typer already uses for the Arguments/Options panels."""

    def format_help(self, ctx: Context, formatter: HelpFormatter) -> None:
        super().format_help(ctx, formatter)
        rich_utils._get_rich_console().print(
            rich_utils.Panel(
                TAGS_HELP.strip(),
                border_style=rich_utils.STYLE_OPTIONS_PANEL_BORDER,
                title="Tags",
                title_align=rich_utils.ALIGN_OPTIONS_PANEL,
            )
        )


app = typer.Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command(
    cls=TagsHelpCommand,
    help="A command-line tool for bulk file renaming and organization using regex.",
)
def _main(
    directory: str = typer.Argument(
        default_factory=os.getcwd,
        show_default=False,
        help="Directory where files are located (default: current directory or `.`).",
    ),
    pattern: str = typer.Argument(
        default="",
        help="Search pattern for renaming (default: '').",
    ),
    replacement: str = typer.Argument(
        default="",
        help="Replacement string for the pattern (default: '').",
    ),
    count: int = typer.Option(
        DEFAULT_OPTIONS["count"],
        "-c",
        "--count",
        help=f"Max replacements per file (default: {DEFAULT_OPTIONS['count']}).",
    ),
    regex: bool = typer.Option(
        DEFAULT_OPTIONS["regex"],
        "-r",
        "--regex",
        help=f"Treats the pattern as a regular expression (default: {DEFAULT_OPTIONS['regex']}).",
    ),
    case_sensitive: bool = typer.Option(
        DEFAULT_OPTIONS["case_sensitive"],
        "--case-sensitive",
        help=f"Make the search case-sensitive (default: {DEFAULT_OPTIONS['case_sensitive']}).",
    ),
    apply_to: str = typer.Option(
        DEFAULT_OPTIONS["apply_to"],
        "--apply-to",
        help=f"Specifies where the renaming should be applied (default: {DEFAULT_OPTIONS['apply_to']}).",
    ),
    exclude: list[str] = typer.Option(
        None,
        "--exclude",
        metavar="PATTERN",
        help="Exclude files matching PATTERN (exact name or glob, e.g. `README.md`, `*.log`). Repeatable; prefix with `!` to re-include a file matched by an earlier pattern.",
    ),
    yes: bool = typer.Option(
        False,
        "-y",
        "--yes",
        help="Apply the rename immediately without opening the TUI (headless mode).",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview the rename without opening the TUI or changing any files (headless mode).",
    ),
    undo: bool = typer.Option(
        False,
        "--undo",
        help="Undo the last rename applied to `directory` without opening the TUI (headless mode).",
    ),
    redo: bool = typer.Option(
        False,
        "--redo",
        help="Redo the last undone rename in `directory` without opening the TUI (headless mode).",
    ),
) -> SimpleNamespace:
    if apply_to not in APPLY_TO_CHOICES:
        raise typer.BadParameter(
            f"invalid choice: {apply_to!r} (choose from {', '.join(APPLY_TO_CHOICES)})",
            param_hint="'--apply-to'",
        )

    return SimpleNamespace(
        directory=directory,
        pattern=pattern,
        replacement=replacement,
        count=count,
        regex=regex,
        case_sensitive=case_sensitive,
        apply_to=apply_to,
        exclude=exclude,
        yes=yes,
        dry_run=dry_run,
        undo=undo,
        redo=redo,
    )


def parse_args() -> SimpleNamespace:
    """Parse and return the command-line arguments."""
    command = get_command(app)
    try:
        # standalone_mode=False so a successful parse returns `_main`'s
        # SimpleNamespace directly instead of click calling sys.exit(0).
        result = command.main(args=sys.argv[1:], standalone_mode=False)
    except UsageError as e:
        e.show()
        sys.exit(e.exit_code)

    # `--help` resolves via click's Exit exception, which command.main()
    # converts to its exit code (an int) rather than raising when
    # standalone_mode is disabled.
    if isinstance(result, int):
        sys.exit(result)

    return result
