import os
from typing import Optional
from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, Input, Checkbox, Select
from textual.containers import (
    Container,
    HorizontalScroll,
    VerticalScroll,
)

from renux.components import Form, Preview
from renux.renamer import apply_renames, get_renames
from renux.constants import DEFAULT_OPTIONS
from renux.ui import CSS_PATH, THEME, BANNER
from renux.bindings import BINDINGS


class RenameApp(App):
    """Main application class."""

    CSS_PATH = str(CSS_PATH)
    BINDINGS = BINDINGS

    def __init__(
        self,
        directory: Optional[str],
        pattern: Optional[str],
        replacement: Optional[str],
        options: Optional[dict],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.directory = directory or os.getcwd()
        self.pattern = pattern or ""
        self.replacement = replacement or ""
        self.options = options or DEFAULT_OPTIONS.copy()

    def on_mount(self) -> None:
        self.register_theme(THEME)
        self.theme = "gruvbox"
        # Focus on the first input field
        self.query_one("#pattern", Input).focus()

    def compose(self) -> ComposeResult:
        yield Footer()
        with HorizontalScroll():
            # Form column
            with VerticalScroll():
                yield Container(Label(BANNER), id="banner")
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
        self.pattern = ""
        self.replacement = ""
        self.options = DEFAULT_OPTIONS
        self.query_one("#pattern", Input).value = ""
        self.query_one("#replacement", Input).value = ""
        self.query_one("#count", Input).value = str(DEFAULT_OPTIONS["count"])
        self.query_one("#regex", Checkbox).value = bool(DEFAULT_OPTIONS["regex"])
        self.query_one("#case_sensitive", Checkbox).value = bool(
            DEFAULT_OPTIONS["case_sensitive"]
        )
        self.query_one("#apply_to", Select).value = DEFAULT_OPTIONS["apply_to"]

    def action_save(self) -> None:
        files = [entry.name for entry in os.scandir(self.directory) if entry.is_file()]
        try:
            renames = get_renames(
                files, self.directory, self.pattern, self.replacement, self.options
            )
            apply_renames(self.directory, renames)

            self.query_one("#pattern", Input).value = ""
            self.query_one("#replacement", Input).value = ""
            self.query_one("#pattern", Input).focus()
            self.show_message("Changes applied successfully.", "success")
        except Exception as e:
            self.show_message(str(e))
        self.query_one(Preview).update_preview()
