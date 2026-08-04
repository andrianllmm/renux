from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Markdown

from renux.constants import TEXT_OPERATIONS

HELP_MARKDOWN = f"""\
# Markup Syntax

Use these placeholders in the **Replace with** field.

## Text transformations
`{{string|operation}}`

operations: {", ".join(f"`{op}`" for op in TEXT_OPERATIONS)}

## Counter
`{{counter(start=1,step=1,padding=1)}}`

e.g. `{{counter(1,2,3)}}` generates `001`, `003`, `005`, ...

## Dates
`{{now|created_at|modified_at(<format>)}}`

`<format>` uses strftime codes, e.g. `{{now(%Y)}}` for the current year.

## Examples
- `file_{{counter}}`
- `file_{{created_at(%Y)}}`
- `{{filename|slugify}}`
"""


class HelpScreen(ModalScreen[None]):
    """Modal screen showing the markup syntax reference."""

    BINDINGS = [
        Binding("escape,f1", "dismiss(None)", "Close", priority=True),
    ]

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="help-container"):
            yield Markdown(HELP_MARKDOWN)
