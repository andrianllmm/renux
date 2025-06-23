import hashlib
import json
import os
import tempfile

BACKUP_DIRNAME = ".renux_backup"


def _get_backup_dir() -> str:
    """Get the path to the backup directory, creating it if necessary."""
    backup_dir = os.path.join(tempfile.gettempdir(), BACKUP_DIRNAME)
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def _get_backup_path(directory: str) -> str:
    """Return a unique backup file path for the given directory."""
    hash_digest = hashlib.sha256(directory.encode()).hexdigest()[:16]
    filename = f"backup_{hash_digest}.json"
    return os.path.join(_get_backup_dir(), filename)


def load_backup(
    directory: str,
) -> tuple[list[list[tuple[str, str]]], list[list[tuple[str, str]]]]:
    """Load undo and redo stacks from a directory-specific backup file."""
    backup_filepath = _get_backup_path(directory)

    if not os.path.exists(backup_filepath):
        return [], []

    try:
        with open(backup_filepath, "r") as f:
            data = json.load(f)
            undo_stack = data.get("undo_stack", [])
            redo_stack = data.get("redo_stack", [])
            return undo_stack, redo_stack
    except (json.JSONDecodeError, IOError):
        return [], []


def save_backup(
    directory: str,
    undo_stack: list[list[tuple[str, str]]],
    redo_stack: list[list[tuple[str, str]]],
    indent: int = 2,
) -> None:
    """Save undo and redo stacks to a directory-specific backup file."""
    backup_filepath = _get_backup_path(directory)
    with open(backup_filepath, "w") as f:
        json.dump(
            {
                "undo_stack": undo_stack,
                "redo_stack": redo_stack,
            },
            f,
            indent=indent,
        )
