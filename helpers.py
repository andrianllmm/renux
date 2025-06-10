import datetime
import os
import re
from constants import (
    COUNTER_KEYWORD,
    DATE_KEYWORDS,
    TEXT_OPERATIONS,
    DATE_FORMATS,
)


def process_counter_placeholder(replacement: str, counters: list[int]) -> str:
    """Replace counter placeholders in the replacement string."""
    # Pattern to match counter markup like {counter(start, step, padding)}
    counter_pattern = re.compile(r"\{counter(?:\((\d+)?,?\s*(\d+)?,?\s*(\d+)?\))?\}")

    # Replace each placeholder with the appropriate counter value
    def replace_counter(match: re.Match, i: int) -> str:
        step = int(match.group(2) or 1)
        padding = int(match.group(3) or 1)

        # Get the current counter, formatted with the appropriate padding
        formatted_counter = str(counters[i]).zfill(padding)

        # Increment the counter for the next placeholder
        counters[i] += step

        return formatted_counter

    # Go over the matches and process each one with its index
    for i, match in enumerate(counter_pattern.finditer(replacement)):
        replacement = replacement.replace(match.group(0), replace_counter(match, i), 1)

    return replacement


def process_date_placeholders(replacement: str, file_name: str, directory: str) -> str:
    """Replace date-related placeholders with actual formatted dates."""
    file_path = os.path.join(directory, file_name)

    # Pattern to match date markup like {now(%Y-%m-%d)}
    date_pattern = re.compile(r"\{(now|created_at|modified_at)(?:\((.+)\))?\}")

    def replace_date(match):
        date_type = match.group(1) or ""
        date_format = match.group(2) or "%Y-%m-%d"

        # Get the corresponding date
        if date_type == "now":
            return datetime.datetime.now().strftime(date_format)
        elif date_type == "created_at":
            created_time = os.path.getctime(file_path)
            return datetime.datetime.fromtimestamp(created_time).strftime(date_format)
        elif date_type == "modified_at":
            modified_time = os.path.getmtime(file_path)
            return datetime.datetime.fromtimestamp(modified_time).strftime(date_format)

    # Replace all date-related placeholders with actual dates
    return date_pattern.sub(replace_date, replacement)


def apply_text_operations(text: str) -> str:
    """Apply case transformations using markup like {<group>|<operation>}."""
    # Pattern to match markup like {<group>|<operation>}
    markup_pattern = re.compile(r"\{([^|]+)\|([^\}]+)\}")

    def transform_match(match: re.Match) -> str:
        group = match.group(1)  # The group reference (e.g., \1)
        operation_type = match.group(2)  # The operation to apply (e.g., slugify)

        operation = TEXT_OPERATIONS.get(operation_type, lambda s: s)
        return operation(group)

    # Replace all transformations in the text
    return markup_pattern.sub(transform_match, text)


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
