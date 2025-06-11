from slugify import slugify
from typing import Callable


DEFAULT_OPTIONS: dict[str, str | int | bool] = {
    "count": 0,
    "regex": True,
    "case_sensitive": False,
    "apply_to": "name",
}

APPLY_TO_LABELS = {
    "Filename only": "name",
    "Extension only": "ext",
    "Filename + Extension": "both",
}
APPLY_TO_OPTIONS = [(label, key) for label, key in APPLY_TO_LABELS.items()]

TEXT_OPERATIONS: dict[str, Callable[[str], str]] = {
    "capitalize": str.capitalize,
    "len": lambda s: str(len(s)),
    "lower": str.lower,
    "reverse": lambda s: s[::-1],
    "slugify": slugify,
    "strip": str.strip,
    "swapcase": str.swapcase,
    "title": str.title,
    "upper": str.upper,
}

COUNTER_KEYWORD = "counter"

DATE_KEYWORDS = ["now", "created_at", "modified_at"]

DATE_FORMATS = [
    "",
    "(%Y)",
    "(%Y-%m-%d)",
    "(%d-%m-%Y)",
    "(%m-%d-%Y)",
    "(%H:%M:%S)",
    "(%Y-%m-%d %H:%M:%S)",
    "(%d-%m-%Y %H:%M:%S)",
    "(%m-%d-%Y %H:%M:%S)",
]
