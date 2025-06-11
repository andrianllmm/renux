import datetime
import os
import re

from renux.constants import (
    DEFAULT_OPTIONS,
    TEXT_OPERATIONS,
)


def apply_renames(directory: str, renames: list[tuple[str, str]]) -> None:
    """Apply the renaming changes."""
    # Abort if no files need renaming
    if sum(1 for f in renames if f[0] != f[1]) <= 0:
        raise ValueError("No files to rename. Try again.")

    # Check for potential duplicate file names
    seen = set()
    for _, new_name in renames:
        if new_name in seen:
            raise ValueError("There will be duplicate files. Try again.")
        seen.add(new_name)

    # Apply the renaming changes
    for old_name, new_name in renames:
        # Skip unchanged files
        if old_name == new_name:
            continue

        # Construct full paths
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)

        # Attempt to rename the file
        try:
            os.rename(old_path, new_path)
        except FileExistsError as e:
            continue
        except PermissionError as e:
            continue
        except Exception as e:
            continue


def get_renames(
    files: list[str],
    directory: str,
    pattern: str,
    replacement: str,
    options: dict,
) -> list[tuple[str, str]]:
    """Rename multiple files in a directory based on specified search and replacement criteria."""
    # Initialize counters for placeholder replacement
    counters = []
    counter_pattern = r"\{counter(?:\((\d+)?,?\s*(\d+)?,?\s*(\d+)?\))?\}"
    for match in re.findall(counter_pattern, replacement):
        start = int(match[0] if len(match) > 0 and match[0] else 1)
        counters.append(start)

    # Store the original and new name of each file
    renames: list[tuple[str, str]] = []
    for file_name in files:
        try:
            new_name = get_rename(
                file_name,
                directory,
                pattern,
                replacement,
                options,
                counters,
            )
        except re.error as e:
            continue
        except Exception as e:
            continue
        renames.append((file_name, new_name))

    return renames


def get_rename(
    file_name: str,
    directory: str,
    pattern: str,
    replacement: str,
    options: dict,
    counters: list[int] = [],
) -> str:
    """Generate a new file name by applying the search pattern and replacement rules."""
    options = {**DEFAULT_OPTIONS, **options}  # options overrides DEFAULT_OPTIONS

    flags = 0

    if not options["regex"]:
        pattern = re.escape(pattern)

    if not options["case_sensitive"]:
        flags |= re.IGNORECASE

    # Abort if no match is found for the pattern
    if not re.search(pattern, file_name, flags):
        return file_name

    # Process placeholders in the replacement string
    replacement = process_counter_placeholder(replacement, counters)
    replacement = process_date_placeholders(replacement, file_name, directory)

    # Apply renaming based on the target (file name, extension, or both)
    name, ext = os.path.splitext(file_name)

    if options["apply_to"] == "name":
        new_name = (
            re.sub(pattern, replacement, name, options["count"], flags=flags) + ext
        )
    elif options["apply_to"] == "ext":
        new_name = (
            name
            + "."
            + re.sub(pattern, replacement, ext[1:], options["count"], flags=flags)
        )
    else:
        new_name = re.sub(
            pattern, replacement, file_name, options["count"], flags=flags
        )

    # Apply additional text operations
    new_name = apply_text_operations(new_name)

    return new_name


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
