from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Markdown

from renux.tags_reference import render_markdown

HELP_MARKDOWN = render_markdown()


class HelpScreen(ModalScreen[None]):
    """Modal screen showing the tags reference."""

    BINDINGS = [
        Binding("escape,f1", "dismiss(None)", "Close", priority=True),
    ]

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="help-container"):
            yield Markdown(HELP_MARKDOWN)
