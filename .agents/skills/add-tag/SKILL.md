---
name: add-tag
description: Scaffold a new renux tag placeholder or filter (e.g. "{counter}" or "{name|upper}"), keeping the registry, README, and tests in sync. Use when asked to add a new placeholder or filter to renux.
---

# add-tag

Adds a new `{placeholder}` or `{value|filter}` to renux. The registry in
`src/renux/tags.py` is the single source of truth. README docs and
autocomplete are generated from it, so registering it correctly there is
almost the whole job.

## Steps

1. Read `src/renux/tags.py` to see the `Placeholder`/`Filter` dataclasses and
   a couple of existing `register_placeholder`/`register_filter` calls for
   the pattern to follow.
2. Add the new placeholder or filter:
   - **Placeholder**: needs `name`, `description`, `syntax`, a `resolve`
     function taking `PlaceholderContext`, `category`, and ideally an
     `example` and suggested `(args)` strings for autocomplete.
   - **Filter**: needs `name`, `func` (`str -> str`), and `description`.
3. If the resolve/filter logic is non-trivial, put it in
   `src/renux/helpers/` (see `helpers/casing.py` for the existing pattern)
   and import it into `tags.py`.
4. Add a test case in `tests/test_tags.py` covering the new placeholder or
   filter (normal input, and any edge case like empty args or empty string).
5. Regenerate the README's auto-generated tags section:
   ```sh
   poetry run python scripts/sync_readme.py
   ```
   This rewrites the block between `<!-- TAGS:START -->` and
   `<!-- TAGS:END -->`. Do not hand-edit that block.
6. Run the full check before considering it done:
   ```sh
   poetry run pytest
   poetry run mypy src
   ```

## Don't

- Don't hand-edit the README's tags block. It's overwritten by
  `sync_readme.py` and by the `sync-readme` pre-commit hook.
- Don't duplicate placeholder/filter docs anywhere else; everything derives
  from `tags.py` via `src/renux/tags_reference.py`.
