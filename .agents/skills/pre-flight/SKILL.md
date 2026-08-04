---
name: pre-flight
description: Run renux's full pre-commit checklist (tests, type check, format, lint, README sync) before committing. Use before committing changes or when asked to check/verify the repo is ready to commit.
---

# pre-flight

Runs the same checks CI and the pre-commit hooks enforce, so problems are
caught before a commit attempt fails partway through.

## Steps

Run in order, fixing failures as you go:

1. Tests
   ```sh
   poetry run pytest
   ```
2. Type check
   ```sh
   poetry run mypy src
   ```
3. Format and lint
   ```sh
   poetry run black .
   poetry run isort .
   ```
4. README sync. Required if `src/renux/tags.py` or
   `src/renux/tags_reference.py` changed:
   ```sh
   poetry run python scripts/sync_readme.py
   ```
   If it prints "README.md tags reference updated.", re-stage README.md.
5. Re-check `git status`/`git diff` for anything the above steps modified
   (formatting, README) before committing.

## Notes

- Commit messages must follow Conventional Commits (enforced by the
  commitizen `commit-msg` hook).
  Use `poetry run cz commit` for a guided prompt if unsure.
- Don't bypass any of this with `git commit --no-verify`.
