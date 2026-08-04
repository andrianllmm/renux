import re

from rich.highlighter import Highlighter
from rich.text import Text

from renux.tags import FILTERS, PLACEHOLDERS

_KEYWORDS = "|".join(re.escape(name) for name in PLACEHOLDERS)
_OPERATIONS = "|".join(re.escape(name) for name in FILTERS)

TOKEN_PATTERN = re.compile(
    r"(?P<punctuation>[{}()])"
    rf"|(?P<keyword>\b(?:{_KEYWORDS})\b)"
    rf"|(?P<operation>\|(?:{_OPERATIONS})\b)"
)


class TokenHighlighter(Highlighter):
    """Highlights renux's placeholder syntax, e.g. `{counter()}`, `{now(%Y)}`, `{name|upper}`."""

    def __init__(self, keyword: str, operation: str, punctuation: str = "dim") -> None:
        self.styles = {
            "punctuation": punctuation,
            "keyword": keyword,
            "operation": operation,
        }
        super().__init__()

    def highlight(self, text: Text) -> None:
        for match in TOKEN_PATTERN.finditer(text.plain):
            group = match.lastgroup
            if group is not None:
                text.stylize(self.styles[group], *match.span())
