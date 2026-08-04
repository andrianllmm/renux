import os

from renux.app import RenameApp
from renux.backup import load_backup, save_backup
from renux.helpers.files import get_files
from renux.parser import parse_args
from renux.renamer import apply_renames, get_renames
from renux.ui import CONSOLE


def run_headless(
    directory: str, pattern: str, replacement: str, options: dict, dry_run: bool
) -> None:
    """Compute and (unless dry-run) apply renames without opening the TUI."""
    files = get_files(directory)
    renames = get_renames(files, directory, pattern, replacement, options)
    changed = [(old, new) for old, new in renames if old != new]

    if not changed:
        CONSOLE.print("No files to rename.", style="yellow")
        return

    for old_name, new_name in changed:
        CONSOLE.print(f"{old_name} -> {new_name}")

    if dry_run:
        return

    try:
        apply_renames(directory, renames)
    except ValueError as e:
        CONSOLE.print(str(e), style="red")
        return

    undo_stack, redo_stack = load_backup(directory)
    undo_stack.append(renames)
    redo_stack.clear()
    save_backup(directory, undo_stack, redo_stack)

    CONSOLE.print(f"Renamed {len(changed)} file(s).", style="green")


def run_undo(directory: str) -> None:
    """Undo the last rename applied to `directory` without opening the TUI."""
    undo_stack, redo_stack = load_backup(directory)

    if not undo_stack:
        CONSOLE.print("Nothing to undo.", style="yellow")
        return

    last_renames = undo_stack.pop()

    try:
        reversed_renames = [(new, old) for old, new in last_renames]
        apply_renames(directory, reversed_renames)
        redo_stack.append(last_renames)
        CONSOLE.print("Undo successful.", style="green")
    except Exception as e:
        CONSOLE.print(f"Undo failed: {e}", style="red")

    save_backup(directory, undo_stack, redo_stack)


def run_redo(directory: str) -> None:
    """Redo the last undone rename in `directory` without opening the TUI."""
    undo_stack, redo_stack = load_backup(directory)

    if not redo_stack:
        CONSOLE.print("Nothing to redo.", style="yellow")
        return

    renames = redo_stack.pop()

    try:
        apply_renames(directory, renames)
        undo_stack.append(renames)
        CONSOLE.print("Redo successful.", style="green")
    except Exception as e:
        CONSOLE.print(f"Redo failed: {e}", style="red")

    save_backup(directory, undo_stack, redo_stack)


def main() -> None:
    """Main entry point of the script."""
    # Parse command-line arguments
    args = parse_args()

    directory = args.directory
    if not os.path.isdir(directory):
        CONSOLE.print(f"Directory `{directory}` does not exist.", style="red")
        return
    # Headless mode: undo/redo the last rename directly and exit, no TUI
    if args.undo:
        run_undo(directory)
        return
    if args.redo:
        run_redo(directory)
        return

    pattern = args.pattern
    replacement = args.replacement
    options = {
        "count": args.count,
        "regex": args.regex,
        "case_sensitive": args.case_sensitive,
        "apply_to": args.apply_to,
    }

    # Headless mode: apply/preview the rename directly and exit, no TUI
    if args.yes or args.dry_run:
        run_headless(directory, pattern, replacement, options, dry_run=args.dry_run)
        return

    # Run the app
    app = RenameApp(
        directory=directory, pattern=pattern, replacement=replacement, options=options
    )
    app.run()


if __name__ == "__main__":
    main()
