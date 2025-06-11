import os
from typing import TYPE_CHECKING
from rich.highlighter import RegexHighlighter
from textual.widget import Widget
from textual.widgets import Input, Checkbox, Select, Label
from textual.validation import Number
from textual.suggester import SuggestFromList
from textual.containers import Horizontal

from renux.constants import APPLY_TO_OPTIONS
from renux.helpers import get_keywords

if TYPE_CHECKING:
    from renux.app import RenameApp


class Form(Widget):
    """Form widget for renaming files."""

    app: "RenameApp"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = [
            entry.name for entry in os.scandir(self.app.directory) if entry.is_file()
        ]
        self.keywords = get_keywords()

    def compose(self):
        yield Input(
            id="pattern",
            value=self.app.pattern,
            placeholder="Search for",
            compact=True,
            highlighter=RegexHighlighter(),
            suggester=SuggestFromList(self.files, case_sensitive=False),
        )
        yield Input(
            id="replacement",
            value=self.app.replacement,
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
                value=str(self.app.options.get("count", 0)),
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
            value=self.app.options["regex"],
            compact=True,
            classes="w-100",
        )
        yield Checkbox(
            "Case sensitive",
            id="case_sensitive",
            value=self.app.options["case_sensitive"],
            compact=True,
            classes="w-100",
        )
        yield Select(
            id="apply_to",
            value=self.app.options["apply_to"],
            options=APPLY_TO_OPTIONS,
            compact=True,
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id in ("pattern", "replacement"):
            setattr(self.app, event.input.id, event.value)
        elif event.input.id == "count":
            self.app.options["count"] = int(event.value or "0")

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self._update_option(event.checkbox.id, event.value)

    def on_select_changed(self, event: Select.Changed) -> None:
        self._update_option(event.select.id, event.value)

    def _update_option(self, key: str | None, value) -> None:
        if key is not None and key in self.app.options:
            self.app.options[key] = value
