import fnmatch
import os


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


def is_excluded(file_name: str, patterns: list[str]) -> bool:
    """Check whether `file_name` matches any of the given exclude patterns
    (exact names or globs, e.g. `README.md`, `*.log`).

    Patterns are evaluated in order, gitignore-style: a pattern prefixed with
    `!` re-includes a file that matched an earlier pattern, so later patterns
    take precedence (e.g. `["*.txt", "!foo1.txt"]` excludes all `.txt` files
    except `foo1.txt`)."""
    excluded = False
    for pattern in patterns:
        if pattern.startswith("!"):
            if fnmatch.fnmatch(file_name, pattern[1:]):
                excluded = False
        elif fnmatch.fnmatch(file_name, pattern):
            excluded = True
    return excluded


def filter_excluded(files: list[str], patterns: list[str]) -> list[str]:
    """Return `files` with any entries matching an exclude pattern removed."""
    if not patterns:
        return files
    return [f for f in files if not is_excluded(f, patterns)]
