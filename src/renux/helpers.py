import os

from renux.constants import (
    TEXT_OPERATIONS,
    COUNTER_KEYWORD,
    DATE_KEYWORDS,
    DATE_FORMATS,
)


def get_files(directory: str) -> list[str]:
    """Get all files in the directory, sorted alphabetically (case-insensitive)."""
    return sorted(
        [
            entry.name
            for entry in os.scandir(directory)
            if entry.is_file() and entry.name
        ],
        key=lambda name: name.lower(),
    )


def get_keywords() -> list[str]:
    """Get all keywords used in the form."""
    keywords = []
    keywords.extend([f"|{key}" for key in TEXT_OPERATIONS.keys()])
    keywords.extend(
        [
            f"{{{COUNTER_KEYWORD}}}",
            f"{{{COUNTER_KEYWORD}(1,1,0)}}",
            f"{{{COUNTER_KEYWORD}(0,1,0)}}",
        ]
    )
    keywords.extend(
        [f"{{{key}{fmt}}}" for key in DATE_KEYWORDS for fmt in DATE_FORMATS]
    )
    return keywords
