import os
from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, Input, Checkbox, Select
from textual.containers import (
    Container,
    HorizontalScroll,
    VerticalScroll,
)

from renux.renamer import apply_renames, get_renames
from renux.components import Form, Preview
from renux.ui import CSS_PATH, THEME
from renux.bindings import BINDINGS
from renux.constants import DEFAULT_OPTIONS
from renux.helpers import get_files


class RenameApp(App):
    """Main application class."""

    CSS_PATH = str(CSS_PATH)
    BINDINGS = BINDINGS

    def __init__(
        self,
        directory: str = os.getcwd(),
        pattern: str = "",
        replacement: str = "",
        options: dict[str, str | int | bool] = DEFAULT_OPTIONS.copy(),
        *args,
        **kwargs,
    ):
        if directory is None:
            raise ValueError("Both directory must be provided.")

        super().__init__(*args, **kwargs)

        self.undo_stack: list[list[tuple[str, str]]] = []
        self.redo_stack: list[list[tuple[str, str]]] = []

        self.directory = directory
        self.pattern = pattern
        self.replacement = replacement
        self.options = options

        self.files = get_files(directory)
        self.disabled_files: list[str] = []

    def on_mount(self) -> None:
        self.register_theme(THEME)
        self.theme = "gruvbox"
        # Focus on the first input field
        self.query_one("#pattern", Input).focus()

    def compose(self) -> ComposeResult:
        yield Footer()
        with HorizontalScroll():
            # Form column
            with VerticalScroll(id="form-column"):
                yield Container(
                    Label(id="message"),
                    classes="align-center",
                )
                yield Form(id="form")
            # Preview column
            with VerticalScroll(id="preview-column"):
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
        self.pattern = ""
        self.replacement = ""
        self.options = DEFAULT_OPTIONS.copy()
        self.query_one("#pattern", Input).value = ""
        self.query_one("#replacement", Input).value = ""
        self.query_one("#count", Input).value = str(DEFAULT_OPTIONS["count"])
        self.query_one("#regex", Checkbox).value = bool(DEFAULT_OPTIONS["regex"])
        self.query_one("#case_sensitive", Checkbox).value = bool(
            DEFAULT_OPTIONS["case_sensitive"]
        )
        self.query_one("#apply_to", Select).value = DEFAULT_OPTIONS["apply_to"]

    def action_save(self) -> None:
        files = [file for file in self.files if file not in self.disabled_files]
        try:
            renames = get_renames(
                files, self.directory, self.pattern, self.replacement, self.options
            )
            self.undo_stack.append(renames)
            apply_renames(self.directory, renames)

            self.files = get_files(self.directory)
            self.disabled_files.clear()
            self.redo_stack.clear()

            self.query_one("#pattern", Input).value = ""
            self.query_one("#replacement", Input).value = ""
            self.query_one("#pattern", Input).focus()
            self.show_message("Changes applied successfully.", "success")
        except Exception as e:
            self.show_message(str(e))

        self.query_one(Preview).update_preview()

    def action_undo(self) -> None:
        if not self.undo_stack:
            self.show_message("Nothing to undo.", "error")
            return

        last_renames = self.undo_stack.pop()

        try:
            reversed_renames = [(new, old) for old, new in last_renames]
            apply_renames(self.directory, reversed_renames)
            self.redo_stack.append(last_renames)
            self.show_message("Undo successful.", "success")
        except Exception as e:
            self.show_message(f"Undo failed: {e}", "error")

        self.files = get_files(self.directory)
        self.disabled_files.clear()
        self.query_one(Preview).update_preview()

    def action_redo(self) -> None:
        if not self.redo_stack:
            self.show_message("Nothing to redo.", "error")
            return

        renames = self.redo_stack.pop()

        try:
            apply_renames(self.directory, renames)
            self.undo_stack.append(renames)
            self.show_message("Redo successful.", "success")
        except Exception as e:
            self.show_message(f"Redo failed: {e}", "error")

        self.files = get_files(self.directory)
        self.disabled_files.clear()
        self.query_one(Preview).update_preview()
