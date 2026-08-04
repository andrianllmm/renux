import os
import re

from renux.constants import DEFAULT_OPTIONS
from renux.markup import FILTERS, PLACEHOLDERS, PlaceholderContext


def _placeholder_pattern(*, stateful: bool) -> re.Pattern:
    """Regex matching `{name}` / `{name(args)}` for placeholders with the given statefulness."""
    names = [p.name for p in PLACEHOLDERS.values() if p.stateful == stateful]
    if not names:
        return re.compile(r"(?!)")  # never matches
    alternation = "|".join(re.escape(name) for name in names)
    return re.compile(rf"\{{({alternation})(?:\((.*?)\))?\}}")


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
    # Initialize counters for stateful placeholders (e.g. {counter(...)})
    counters = []
    for match in _placeholder_pattern(stateful=True).finditer(replacement):
        name, args = match.group(1), match.group(2) or ""
        placeholder = PLACEHOLDERS[name]
        initial = placeholder.initial(args) if placeholder.initial else 1
        counters.append(initial)

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
    """Replace stateful placeholders (e.g. {counter(...)}) in the replacement string."""
    pattern = _placeholder_pattern(stateful=True)
    index = 0

    def replace(match: re.Match) -> str:
        nonlocal index
        name, args = match.group(1), match.group(2) or ""
        placeholder = PLACEHOLDERS[name]

        current = counters[index]
        ctx = PlaceholderContext(args=args, counter=current, file_name="", directory="")
        result = placeholder.resolve(ctx)

        counters[index] = (
            placeholder.advance(args, current) if placeholder.advance else current
        )
        index += 1

        return result

    return pattern.sub(replace, replacement)


def process_date_placeholders(replacement: str, file_name: str, directory: str) -> str:
    """Replace non-stateful placeholders (e.g. {now}, {created_at}) with resolved values."""
    pattern = _placeholder_pattern(stateful=False)

    def replace(match: re.Match) -> str:
        name, args = match.group(1), match.group(2) or ""
        placeholder = PLACEHOLDERS[name]
        ctx = PlaceholderContext(
            args=args, counter=None, file_name=file_name, directory=directory
        )
        return placeholder.resolve(ctx)

    return pattern.sub(replace, replacement)


def apply_text_operations(text: str) -> str:
    """Apply text transformations using markup like {<group>|<filter>}."""
    # Pattern to match markup like {<group>|<filter>}
    markup_pattern = re.compile(r"\{([^|]+)\|([^\}]+)\}")

    def transform_match(match: re.Match) -> str:
        group = match.group(1)  # The group reference (e.g., \1)
        filter_name = match.group(2)  # The filter to apply (e.g., slugify)

        filter_ = FILTERS.get(filter_name)
        return filter_.func(group) if filter_ else group

    # Replace all transformations in the text
    return markup_pattern.sub(transform_match, text)
