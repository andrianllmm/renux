import os
import re
from typing import Optional
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
from textual.validation import Number
from textual.suggester import SuggestFromList

from constants import DEFAULT_OPTIONS, APPLY_TO_OPTIONS
from helpers import (
    apply_text_operations,
    process_counter_placeholder,
    process_date_placeholders,
    get_keywords,
)
from parser import get_argparser
from ui import console, theme, banner
from bindings import BINDINGS


# Global variables
directory = os.getcwd()
pattern, replacement = "", ""
options = DEFAULT_OPTIONS


class RenameApp(App):
    """Main application class."""

    CSS_PATH = "styles.tcss"
    BINDINGS = BINDINGS

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
        self.query_one("#pattern", Input).value = ""
        self.query_one("#replacement", Input).value = ""
        self.query_one("#count", Input).value = str(DEFAULT_OPTIONS["count"])
        self.query_one("#regex", Checkbox).value = DEFAULT_OPTIONS["regex"]
        self.query_one("#case_sensitive", Checkbox).value = DEFAULT_OPTIONS[
            "case_sensitive"
        ]
        self.query_one("#apply_to", Select).value = DEFAULT_OPTIONS["apply_to"]

    def action_save(self) -> None:
        files = [entry.name for entry in os.scandir(directory) if entry.is_file()]
        try:
            apply_renames(
                directory, get_renames(files, directory, pattern, replacement, options)
            )
            self.query_one("#pattern", Input).value = ""
            self.query_one("#replacement", Input).value = ""
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
        self.keywords = get_keywords()

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
                value=str(options.get("count", 0)),
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
            options=APPLY_TO_OPTIONS,
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
            options["count"] = int(value or "0")

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
    args = get_argparser(
        directory=directory, pattern=pattern, replacement=replacement, options=options
    ).parse_args()

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


if __name__ == "__main__":
    main()
