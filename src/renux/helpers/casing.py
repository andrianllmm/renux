import re


def split_words(s: str) -> list[str]:
    "Split camelCase, PascalCase, snake_case, kebab-case, and space-delimited into words."
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s)  # camel → space
    s = re.sub(r"[-_]", " ", s)  # snake/kebab → space
    return s.strip().split()


def to_camel_case(s: str) -> str:
    """Convert a string to camelCase."""
    parts = split_words(s)
    return parts[0].lower() + "".join(word.capitalize() for word in parts[1:])


def to_pascal_case(s: str) -> str:
    """Convert a string to PascalCase."""
    parts = split_words(s)
    return "".join(word.capitalize() for word in parts)


def to_snake_case(s: str) -> str:
    """Convert a string to snake_case."""
    parts = split_words(s)
    return "_".join(word.lower() for word in parts if word)


def to_kebab_case(s: str) -> str:
    """Convert a string to kebab-case."""
    parts = split_words(s)
    return "-".join(word.lower() for word in parts if word)
