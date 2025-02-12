import os
import re
import argparse
import datetime
from rich.console import Console
from rich.theme import Theme
from rich.text import Text
from rich.tree import Tree
from rich.prompt import Confirm
from slugify import slugify
from typing import Callable


# Custom console theme for displaying messages
custom_theme = Theme(
    {
        "success": "green",
        "error": "red",
        "warning": "yellow",
        "muted": "grey50",
    }
)
console = Console(theme=custom_theme)


def main() -> None:
    """Main entry point of the script."""
    # Parse command-line arguments
    args = parse_arguments()

    # Validate the directory path
    if not os.path.isdir(args.directory):
        console.print(f"Directory {args.directory} does not exist.", style="error")
        return

    # Get list of file names in the specified directory
    files = [entry.name for entry in os.scandir(args.directory) if entry.is_file()]

    # Perform file renaming
    rename_files(
        files,
        args.directory,
        args.pattern,
        args.replacement,
        args.count,
        args.case_sensitive,
        args.regex,
        args.apply_to,
    )


def rename_files(
    files: list[str],
    directory: str,
    pattern: str,
    replacement: str,
    count: int = 0,
    case_sensitive: bool = False,
    use_regex: bool = False,
    apply_to: str = "name",
) -> bool:
    """Rename multiple files in a directory based on specified search and replacement criteria."""
    # Initialize a tree structure to display the file changes
    file_tree = Tree(directory)

    # Initialize counters for placeholder replacement
    counters = []
    counter_pattern = r"\{counter(?:\((\d+)?,?\s*(\d+)?,?\s*(\d+)?\))?\}"
    for match in re.findall(counter_pattern, replacement):
        start = int(match[0] if len(match) > 0 and match[0] else 1)
        counters.append(start)

    # Store the original and new name of each file
    renamed_files: list[tuple[str, str]] = []
    for file_name in files:
        new_name = get_rename(
            file_name,
            directory,
            pattern,
            replacement,
            count,
            case_sensitive,
            use_regex,
            apply_to,
            counters,
        )
        renamed_files.append((file_name, new_name))

        # Update the tree to reflect the changes
        file_text = Text()
        file_text.append(file_name, style="muted")
        file_text.append(" → " if file_name != new_name else "", style="white")
        file_text.append(new_name if file_name != new_name else "", style="cyan")
        file_tree.add(file_text)

    # Summary of renaming actions
    total_files = len(renamed_files)
    total_renamed_files = sum(1 for f in renamed_files if f[0] != f[1])
    console.print(
        f"{total_renamed_files}/{total_files} files will be renamed.",
        highlight=False,
    )

    # Display file renaming results
    console.print("", file_tree, "")

    # Abort if no files need renaming
    if total_renamed_files <= 0:
        console.print("No files to rename. Try again.", style="warning")
        return False

    # Check for potential duplicate file names
    seen = set()
    for _, new_name in renamed_files:
        if new_name in seen:
            console.print("There will be duplicate files. Try again.", style="error")
            return False
        seen.add(new_name)

    # Ask for user confirmation before applying changes
    if not Confirm.ask("Do you want to apply these changes?"):
        console.print("Changes not applied.", style="error")
        return False

    # Apply the renaming changes
    for old_name, new_name in renamed_files:
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
            console.print(
                f"{new_name} already exists. Skipping rename.", style="warning"
            )
            continue
        except PermissionError as e:
            console.print(
                f"Permission error renaming {old_name} -> {new_name}: {e}",
                style="error",
            )
            continue
        except Exception as e:
            console.print(
                f"Error renaming {old_name} -> {new_name}: {e}", style="error"
            )
            continue

    console.print("Changes applied successfully.", style="success")
    return True


def get_rename(
    file_name: str,
    directory: str,
    pattern: str,
    replacement: str,
    count: int = 0,
    case_sensitive: bool = False,
    use_regex: bool = False,
    apply_to: str = "name",
    counters: list[int] = [],
) -> str:
    """Generate a new file name by applying the search pattern and replacement rules."""
    flags = 0
    if not case_sensitive:
        flags |= re.IGNORECASE

    if not use_regex:
        pattern = re.escape(pattern)

    # Abort if no match is found for the pattern
    if not re.search(pattern, file_name, flags):
        return file_name

    # Process placeholders in the replacement string
    replacement = process_counter_placeholder(replacement, counters)
    replacement = process_date_placeholders(replacement, file_name, directory)

    # Apply renaming based on the target (file name, extension, or both)
    name, ext = os.path.splitext(file_name)

    if apply_to == "name":
        new_name = re.sub(pattern, replacement, name, count, flags=flags) + ext
    elif apply_to == "ext":
        new_name = (
            name + "." + re.sub(pattern, replacement, ext[1:], count, flags=flags)
        )
    else:
        new_name = re.sub(pattern, replacement, file_name, count, flags=flags)

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

    # Mapping operations to corresponding functions
    operations: dict[str, Callable[[str], str]] = {
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

    def transform_match(match: re.Match) -> str:
        group = match.group(1)  # The group reference (e.g., \1)
        operation_type = match.group(2)  # The operation to apply (e.g., slugify)

        operation = operations.get(operation_type, lambda s: s)
        return operation(group)

    # Replace all transformations in the text
    return markup_pattern.sub(transform_match, text)


def parse_arguments() -> argparse.Namespace:
    """Parse and return the command-line arguments."""
    parser = argparse.ArgumentParser(
        description="A Python command-line tool for bulk file renaming and organization using regex."
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=os.getcwd(),
        help="Directory where files are located (default is the current directory).",
    )

    parser.add_argument(
        "pattern", help="The search pattern (can be a regular expression)."
    )

    parser.add_argument("replacement", help="The replacement string for the pattern.")

    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=0,
        help="Max replacements per file (default is 0, meaning unlimited).",
    )

    parser.add_argument(
        "-s",
        "--case-sensitive",
        action="store_true",
        help="Make the search case-sensitive (default is False).",
    )

    parser.add_argument(
        "-r",
        "--regex",
        action="store_true",
        help="Use regular expressions in the search pattern (default is False).",
    )

    parser.add_argument(
        "--apply-to",
        choices=["name", "ext", "both"],
        default="name",
        help="Specify where to apply renaming: 'name', 'ext', or 'both' (default is 'name').",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
