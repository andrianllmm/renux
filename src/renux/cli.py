import os

from renux.app import RenameApp
from renux.parser import parse_args
from renux.ui import CONSOLE, THEME


def main() -> None:
    """Main entry point of the script."""
    # Parse command-line arguments
    args = parse_args()

    directory = args.directory
    if not os.path.isdir(directory):
        CONSOLE.print(f"Directory `{directory}` does not exist.", style=THEME.error)
        return
    pattern = args.pattern
    replacement = args.replacement
    options = {
        "count": args.count,
        "regex": args.regex,
        "case_sensitive": args.case_sensitive,
        "apply_to": args.apply_to,
    }

    # Run the app
    app = RenameApp(
        directory=directory, pattern=pattern, replacement=replacement, options=options
    )
    app.run()


if __name__ == "__main__":
    main()
