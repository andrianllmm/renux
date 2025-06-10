from slugify import slugify
from typing import Callable


DEFAULT_OPTIONS = {
    "count": 0,
    "regex": True,
    "case_sensitive": False,
    "apply_to": "name",
}

APPLY_TO_OPTIONS = [
    ("Filename only", "name"),
    ("Extension only", "ext"),
    ("Filename + Extension", "both"),
]

COUNTER_KEYWORD = "counter"
DATE_KEYWORDS = ["now", "created_at", "modified_at"]
TEXT_OPERATIONS: dict[str, Callable[[str], str]] = {
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

DATE_FORMATS = [
    "",
    "(%Y)",
    "(%Y-%m-%d)",
    "(%Y-%m-%d %H:%M:%S)",
    "(%d-%m-%Y)",
    "(%m-%d-%Y)",
]
