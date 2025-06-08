import os
import re
import datetime
from typing import Callable, Optional
from slugify import slugify
from pyfiglet import figlet_format
from argparse import ArgumentParser
from rich.console import Console
from rich.text import Text
from rich.highlighter import RegexHighlighter
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Footer, Label, Input, Checkbox, Select, Tree
from textual.containers import (
    Container,
    Horizontal,
    HorizontalScroll,
    VerticalScroll,
)
from textual.theme import Theme
from textual.binding import Binding
from textual.validation import Number
from textual.suggester import SuggestFromList

DEFAULT_OPTIONS = {
    "count": 0,
    "regex": True,
    "case_sensitive": False,
    "apply_to": "name",
}

# Global variables
directory = os.getcwd()
pattern, replacement = "", ""
options = DEFAULT_OPTIONS
apply_to_options = [
    ("Filename only", "name"),
    ("Extension only", "ext"),
    ("Filename + Extension", "both"),
]

counter_keyword = "counter"
date_keywords = ["now", "created_at", "modified_at"]
text_operations: dict[str, Callable[[str], str]] = {
    "slugify": slugify,
    "upper": str.upper,
    "lower": str.lower,
    "title": str.title,
    "capitalize": str.capitalize,
    "swapcase": str.swapcase,
    "reverse": lambda s: s[::-1],
    "strip": str.strip,
    "len": lambda s: str(len(s)),
}

theme = Theme(
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
banner = figlet_format("RE.NAME", font="smkeyboard")

console = Console()


class CustomParser(ArgumentParser):
    """Custom argument parser."""

    def print_help(self, file=None):
        console.print(Text(banner, style=theme.primary + " bold"))
        return super().print_help(file)


class RenameApp(App):
    """Main application class."""

    CSS_PATH = "styles.tcss"
    BINDINGS = [
        Binding(
            "ctrl+q",
            "quit",
            "Quit",
            priority=True,
            tooltip="Exit the app",
        ),
        Binding("ctrl+s", "save", "Save", priority=True, tooltip="Apply renaming"),
        Binding(
            "ctrl+l", "clear_form", "Clear", priority=True, tooltip="Clear form values"
        ),
        Binding(
            "ctrl+r", "toggle_regex", "Regex", priority=True, tooltip="Toggle regex"
        ),
    ]

    def on_mount(self) -> None:
        self.register_theme(theme)
        self.theme = "gruvbox"
        # Focus on the first input field
        self.query_one("#pattern", Input).focus()

    def compose(self) -> ComposeResult:
        yield Footer()
        with HorizontalScroll():
            # Form column
            with VerticalScroll():
                yield Container(Label(banner), id="banner")
                yield Container(
                    Label(id="message"),
                    classes="align-center",
                )
                yield Form(id="form")
            # Preview column
            with VerticalScroll():
                yield Preview(id="preview")

    def show_message(self, message: str, status: str = "error") -> None:
        error_label = self.query_one("#message", Label)
        error_label.classes = f"text-{status}"
        error_label.update(message)

    def on_input_changed(self, event: Input.Changed) -> None:
        self.query_one(Preview).update_preview()
        self.show_message("")

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self.query_one(Preview).update_preview()
        self.show_message("")

    def on_select_changed(self, event: Select.Changed) -> None:
        self.query_one(Preview).update_preview()
        self.show_message("")

    def action_toggle_regex(self) -> None:
        self.query_one("#regex", Checkbox).toggle()

    def action_clear_form(self) -> None:
        for option in DEFAULT_OPTIONS:
            self.query_one(f"#{option}").value = DEFAULT_OPTIONS[option]

    def action_save(self) -> None:
        files = [entry.name for entry in os.scandir(directory) if entry.is_file()]
        try:
            apply_renames(
                directory, get_renames(files, directory, pattern, replacement, options)
            )
            self.action_clear_form()
            self.query_one("#pattern", Input).focus()
            self.show_message("Changes applied successfully.", "success")
        except Exception as e:
            self.show_message(str(e))
        self.query_one(Preview).update_preview()


class Form(Widget):
    """Form widget for renaming files."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize keywords
        self.files = [entry.name for entry in os.scandir(directory) if entry.is_file()]

        self.text_operations_keywords = [f"|{key}" for key in text_operations.keys()]
        self.counter_keywords = [
            f"{{{counter_keyword}}}",
            f"{{{counter_keyword}(1,1,0)}}",
            f"{{{counter_keyword}(0,1,0)}}",
        ]
        date_formats = [
            "",
            "(%Y)",
            "(%Y-%m-%d)",
            "(%Y-%m-%d %H:%M:%S)",
            "(%d-%m-%Y)",
            "(%m-%d-%Y)",
        ]
        base_date_keywords = ["now", "created_at", "modified_at"]
        self.date_keywords = [
            f"{{{key}{fmt}}}" for key in base_date_keywords for fmt in date_formats
        ]
        self.keywords = (
            self.counter_keywords + self.date_keywords + self.text_operations_keywords
        )

    def compose(self):
        yield Input(
            id="pattern",
            value=pattern,
            placeholder="Search for",
            compact=True,
            highlighter=RegexHighlighter(),
            suggester=SuggestFromList(self.files, case_sensitive=False),
        )
        yield Input(
            id="replacement",
            value=replacement,
            placeholder="Replace with",
            compact=True,
            suggester=SuggestFromList(self.files + self.keywords, case_sensitive=False),
            classes="mb",
        )

        yield Label(
            "[bold]Options[/bold]",
        )
        with Horizontal(classes="h-1"):
            yield Label("Max replacements: ")
            yield Input(
                id="count",
                value=str(options["count"]),
                placeholder="0 for unlimited",
                compact=True,
                type="integer",
                validators=[
                    Number(minimum=0),
                ],
            )
        yield Checkbox(
            "Use regex",
            id="regex",
            value=options["regex"],
            compact=True,
            classes="w-100",
        )
        yield Checkbox(
            "Case sensitive",
            id="case_sensitive",
            value=options["case_sensitive"],
            compact=True,
            classes="w-100",
        )
        yield Select(
            id="apply_to",
            value=options["apply_to"],
            options=apply_to_options,
            compact=True,
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        global pattern, replacement, options
        input_id = event.input.id
        value = event.value
        if input_id == "pattern":
            pattern = value
        elif input_id == "replacement":
            replacement = value
        elif input_id == "count":
            options["count"] = int(value) if value.isdigit() else 0

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        global options
        for key in options.keys():
            if event.checkbox.id == key:
                options[key] = event.value

    def on_select_changed(self, event: Select.Changed) -> None:
        global options
        for key in options.keys():
            if event.select.id == key:
                options[key] = event.value


class Preview(Widget):
    """Tree widget for live preview of renaming changes."""

    tree: Tree = Tree(directory)

    def compose(self):
        self.tree = Tree(directory)
        yield self.tree
        self.update_preview()

    def on_mount(self) -> None:
        self.tree.root.expand()
        self.tree.refresh()

    def update_preview(self) -> None:
        # Get files and their renaming results
        files = [entry.name for entry in os.scandir(directory) if entry.is_file()]
        renamed_files = get_renames(files, directory, pattern, replacement, options)

        self.tree.root.remove_children()
        for old, new in renamed_files:
            if old != new:
                # Indicate the new file name
                text = Text.assemble(
                    (old, "dim"),
                    (" → ", theme.foreground),
                    (new, theme.primary),
                )
            else:
                text = Text(old, style="dim")
            self.tree.root.add(text)
        self.tree.refresh()


def main():
    """Main entry point of the script."""
    global directory, pattern, replacement, options

    # Parse command-line arguments
    parser = get_argparser()
    args = parser.parse_args()

    # Set global variables
    directory = args.directory
    if not os.path.isdir(directory):
        console.print(f"Directory `{directory}` does not exist.", style=theme.error)
        return

    pattern = args.pattern
    replacement = args.replacement
    options = {
        "count": args.count,
        "regex": args.regex,
        "case_sensitive": args.case_sensitive,
        "apply_to": args.apply_to,
    }

    # Run the app
    app = RenameApp()
    app.run()


def apply_renames(directory: str, renamed_files: list[tuple[str, str]]) -> None:
    """Apply the renaming changes."""
    # Abort if no files need renaming
    total_renamed_files = sum(1 for f in renamed_files if f[0] != f[1])
    if total_renamed_files <= 0:
        raise ValueError("No files to rename. Try again.")

    # Check for potential duplicate file names
    seen = set()
    for _, new_name in renamed_files:
        if new_name in seen:
            raise ValueError("There will be duplicate files. Try again.")
        seen.add(new_name)

    # Apply the renaming changes
    for old_name, new_name in renamed_files:
        # Skip unchanged files
        if old_name == new_name:
            continue

        # Construct full paths
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)

        # Attempt to rename the file
        try:
            os.rename(old_path, new_path)
        except FileExistsError as e:
            continue
        except PermissionError as e:
            continue
        except Exception as e:
            continue


def get_renames(
    files: list[str],
    directory: str,
    pattern: str,
    replacement: str,
    options: dict,
) -> list[tuple[str, str]]:
    """Rename multiple files in a directory based on specified search and replacement criteria."""
    # Initialize counters for placeholder replacement
    counters = []
    counter_pattern = r"\{counter(?:\((\d+)?,?\s*(\d+)?,?\s*(\d+)?\))?\}"
    for match in re.findall(counter_pattern, replacement):
        start = int(match[0] if len(match) > 0 and match[0] else 1)
        counters.append(start)

    # Store the original and new name of each file
    renamed_files: list[tuple[str, str]] = []
    for file_name in files:
        try:
            new_name = get_rename(
                file_name,
                directory,
                pattern,
                replacement,
                options,
                counters,
            )
        except re.error as e:
            continue
        except Exception as e:
            continue
        renamed_files.append((file_name, new_name))

    return renamed_files


def get_rename(
    file_name: str,
    directory: str,
    pattern: str,
    replacement: str,
    options: dict,
    counters: Optional[list[int]] = [],
) -> str:
    """Generate a new file name by applying the search pattern and replacement rules."""
    for option in DEFAULT_OPTIONS:
        if option not in options:
            options[option] = DEFAULT_OPTIONS[option]

    flags = 0

    if not options["regex"]:
        pattern = re.escape(pattern)

    if not options["case_sensitive"]:
        flags |= re.IGNORECASE

    # Abort if no match is found for the pattern
    if not re.search(pattern, file_name, flags):
        return file_name

    # Process placeholders in the replacement string
    replacement = process_counter_placeholder(replacement, counters)
    replacement = process_date_placeholders(replacement, file_name, directory)

    # Apply renaming based on the target (file name, extension, or both)
    name, ext = os.path.splitext(file_name)

    if options["apply_to"] == "name":
        new_name = (
            re.sub(pattern, replacement, name, options["count"], flags=flags) + ext
        )
    elif options["apply_to"] == "ext":
        new_name = (
            name
            + "."
            + re.sub(pattern, replacement, ext[1:], options["count"], flags=flags)
        )
    else:
        new_name = re.sub(
            pattern, replacement, file_name, options["count"], flags=flags
        )

    # Apply additional text operations
    new_name = apply_text_operations(new_name)

    return new_name


def process_counter_placeholder(replacement: str, counters: list[int]) -> str:
    """Replace counter placeholders in the replacement string."""
    # Pattern to match counter markup like {counter(start, step, padding)}
    counter_pattern = re.compile(r"\{counter(?:\((\d+)?,?\s*(\d+)?,?\s*(\d+)?\))?\}")

    # Replace each placeholder with the appropriate counter value
    def replace_counter(match: re.Match, i: int) -> str:
        step = int(match.group(2) or 1)
        padding = int(match.group(3) or 1)

        # Get the current counter, formatted with the appropriate padding
        formatted_counter = str(counters[i]).zfill(padding)

        # Increment the counter for the next placeholder
        counters[i] += step

        return formatted_counter

    # Go over the matches and process each one with its index
    for i, match in enumerate(counter_pattern.finditer(replacement)):
        replacement = replacement.replace(match.group(0), replace_counter(match, i), 1)

    return replacement


def process_date_placeholders(replacement: str, file_name: str, directory: str) -> str:
    """Replace date-related placeholders with actual formatted dates."""
    file_path = os.path.join(directory, file_name)

    # Pattern to match date markup like {now(%Y-%m-%d)}
    date_pattern = re.compile(r"\{(now|created_at|modified_at)(?:\((.+)\))?\}")

    def replace_date(match):
        date_type = match.group(1) or ""
        date_format = match.group(2) or "%Y-%m-%d"

        # Get the corresponding date
        if date_type == "now":
            return datetime.datetime.now().strftime(date_format)
        elif date_type == "created_at":
            created_time = os.path.getctime(file_path)
            return datetime.datetime.fromtimestamp(created_time).strftime(date_format)
        elif date_type == "modified_at":
            modified_time = os.path.getmtime(file_path)
            return datetime.datetime.fromtimestamp(modified_time).strftime(date_format)

    # Replace all date-related placeholders with actual dates
    return date_pattern.sub(replace_date, replacement)


def apply_text_operations(text: str) -> str:
    """Apply case transformations using markup like {<group>|<operation>}."""
    # Pattern to match markup like {<group>|<operation>}
    markup_pattern = re.compile(r"\{([^|]+)\|([^\}]+)\}")

    def transform_match(match: re.Match) -> str:
        group = match.group(1)  # The group reference (e.g., \1)
        operation_type = match.group(2)  # The operation to apply (e.g., slugify)

        operation = text_operations.get(operation_type, lambda s: s)
        return operation(group)

    # Replace all transformations in the text
    return markup_pattern.sub(transform_match, text)


def get_argparser() -> CustomParser:
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
        choices=[option[1] for option in apply_to_options],
        default=options["apply_to"],
        help=f"Specifies where the renaming should be applied (default is {options['apply_to']}).",
    )

    return parser


if __name__ == "__main__":
    main()
