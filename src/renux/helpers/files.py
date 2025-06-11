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
