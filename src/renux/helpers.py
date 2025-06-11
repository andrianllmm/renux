from renux.constants import (
    COUNTER_KEYWORD,
    DATE_KEYWORDS,
    TEXT_OPERATIONS,
    DATE_FORMATS,
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
