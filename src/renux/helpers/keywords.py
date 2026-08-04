from renux.tags import FILTERS, PLACEHOLDERS


def get_keywords() -> list[str]:
    """Get all keywords used in the form."""
    keywords = [f"|{name}" for name in FILTERS]
    for placeholder in PLACEHOLDERS.values():
        args_suggestions = placeholder.arg_suggestions or [""]
        keywords.extend(f"{{{placeholder.name}{args}}}" for args in args_suggestions)
    return keywords
