# AGENTS.md

Notes for agents working on renux (TUI bulk file renamer).

## Layout

- `src/renux/tags.py` - placeholder/filter registry (see above)
- `src/renux/parser.py` - resolves tag strings against filenames
- `src/renux/renamer.py` - actual rename/apply logic
- `src/renux/backup.py` - undo/backup support for applied renames
- `src/renux/app.py`, `screens/`, `components/` - Textual TUI
- `src/renux/cli.py` - CLI entrypoint (`renux` console script)

## Testing

`poetry run pytest` and `poetry run mypy src` before considering a change done.
Both are also enforced in CI/preqcommit.

## Tags registry is the source of truth

`src/renux/tags.py` is a single registry for every `{placeholder}` and `{value|filter}`.
Adding/changing a placeholder or filter there is enough.
Docs, autocomplete, and README all derive from it via `src/renux/tags_reference.py`.
Don't hand-edit the tag docs elsewhere.
