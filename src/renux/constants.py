from typing import Callable

from slugify import slugify

from renux.helpers.casing import (
    to_camel_case,
    to_kebab_case,
    to_pascal_case,
    to_snake_case,
)

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
    "slugify": slugify,
    "lower": str.lower,
    "upper": str.upper,
    "caps": str.capitalize,
    "title": str.title,
    "camel": to_camel_case,
    "pascal": to_pascal_case,
    "snake": to_snake_case,
    "kebab": to_kebab_case,
    "swapcase": str.swapcase,
    "reverse": lambda s: s[::-1],
    "strip": str.strip,
    "len": lambda s: str(len(s)),
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
