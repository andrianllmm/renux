---
name: renux
description: Drive the `renux` CLI to bulk-rename files. Covers regex patterns, placeholder tags ({counter}, {now}, {size}, EXIF/video metadata), text filters, and file exclusion. Trigger on any bulk/batch rename or filename cleanup request, even without "renux" named, e.g. "add today's date to these screenshots," "strip the IMG_ prefix," "convert filenames to kebab-case," "number these files."
---

# renux

`renux` is a headless-capable CLI for bulk file renaming: regex search/replace,
placeholder tags, text-transform filters, and gitignore-style exclusion. Your
job is to turn a plain-language rename request into a correct, safe `renux`
invocation, not to write a custom renaming script.

## Why use renux instead of writing a script

renux already handles the fiddly parts correctly: capture groups, EXIF/video
metadata extraction, per-placeholder counters, collision-safe writes, and a
real undo/redo log. A hand-rolled `os.rename` loop reproduces all of that
worse and has no undo. If `renux` isn't installed, check for it
(`renux --version`) and offer to install it (`pipx install renux` or
`pip install renux`) before falling back to anything else.

## Command shape

```sh
renux [directory] [pattern] [replacement] [options]
```

- `directory`: where the files live (default `.`).
- `pattern`: what to match, literal text or regex (regex is on by default).
- `replacement`: what to put in its place, literal text and/or `{tags}`.

Key options:

| Flag | Meaning |
| ---- | ------- |
| `-c, --count N` | max replacements per file (default 0, unlimited) |
| `-r, --regex` | treat pattern as regex (default on) |
| `--case-sensitive` | case-sensitive match (default off) |
| `--apply-to name\|ext\|both` | what part of the filename to touch (default `name`) |
| `--exclude PATTERN` | skip matching files, repeatable, gitignore-style. `!pattern` re-includes, e.g. `--exclude "*.log" --exclude "!keep.log"` |
| `-y, --yes` | apply immediately, headless, no TUI |
| `--dry-run` | preview only, headless, no TUI, no writes |
| `--undo` | undo the last rename applied to `directory` |
| `--redo` | redo the last undone rename in `directory` |

Full tag/filter reference (placeholders like `{counter}`, `{now(...)}`,
`{size}`, EXIF/video tags, and filters like `|slugify`, `|snake`, `|title`)
is in `references/tags.md`. Read it whenever the request involves anything
beyond a plain literal replacement. Don't guess tag syntax.

## Workflow

1. **Translate the request into pattern/replacement/options.** If the user
   wants to _transform_ existing names rather than replace a fixed
   substring (e.g. "make these kebab-case," "strip everything after the
   first underscore"), you likely need a capturing regex pattern paired
   with a backreference and filter in the replacement. See
   `references/tags.md` for the syntax and examples. If they want to _add_
   something (a date, a counter, a size), anchor the pattern to the
   position and put the tag in the replacement.
2. **Scope it.** Confirm or infer the target directory. If the user
   mentions a subset (photos only, a specific extension, "except the
   drafts"), express that with `--apply-to`, a narrower `pattern`, and/or
   `--exclude`. Don't silently widen scope to a whole directory tree if
   they described a subset.
3. **Dry-run first, always.** Run with `--dry-run` before ever touching
   real files:
   ```sh
   renux ./photos "IMG_(\d+)" "vacation_\1" --dry-run
   ```
   Read the printed preview (old name to new name for every affected
   file). Sanity-check it yourself: did it match the files the user meant,
   skip the ones they didn't, and produce names that look right? If
   anything's off, adjust the command and dry-run again rather than
   guessing twice.
4. **Show the user the preview and get confirmation before applying.** A
   bulk rename touches many files at once and deserves the same
   confirm-before-acting treatment as any other hard-to-reverse action.
   Skip this only if the user has already explicitly pre-approved applying
   directly (e.g. "just do it, no need to check with me").
5. **Apply with `-y`** once confirmed:
   ```sh
   renux ./photos "IMG_(\d+)" "vacation_\1" -y
   ```
6. **If something goes wrong after applying**, use `renux <directory> --undo`
   immediately. It reverts the last rename batch in that directory. Mention
   this safety net exists rather than trying to manually reconstruct
   original names.

## Common request patterns

- **Prefix/suffix add** (date, counter, tag): anchor pattern to `^` (start)
  or `$` (end), put the tag in the replacement. An empty pattern (`""`) is
  a no-op in renux; it aborts before matching anything.
  ```sh
  renux ./screenshots "^" "{now(%Y-%m-%d)}_" -y
  renux ./exports "$" "_{counter(1,1,3)}" -y
  ```
- **Strip/replace a substring**: literal or regex pattern, literal
  replacement.
  ```sh
  renux ./photos "IMG_" "" -y
  ```
- **Case/format conversion**: capture the whole stem with `(.*)`, then
  reference it in the replacement as `{\1|filter}`. The backreference must
  sit inside the braces with the filter, not a bare word (see
  `references/tags.md` for a verified pitfall here).
  ```sh
  renux ./docs "(.*)" "{\1|kebab}" -r -y
  ```
- **Change extension only**: `--apply-to ext`. The pattern then matches the
  extension without its leading dot (`"txt"`, not `".txt"`).
  ```sh
  renux ./notes "txt" "md" --apply-to ext -y
  ```
- **Exclude a subset**: layer `--exclude`, remembering `!` re-includes.
  ```sh
  renux . "(.*)" "{\1|slugify}" -r --exclude "*.tmp" --exclude "!keep.tmp" -y
  ```

## Guardrails

- Never run without `--dry-run` first, and never apply (`-y`) without the
  user seeing and approving the dry-run preview. Bulk renames touch many
  files at once, and a bad regex can silently clobber names or cause
  collisions.
- Don't invent tag/filter syntax from memory; check `references/tags.md`.
  A wrong tag name fails loudly (literal text in the output), but a wrong
  filter or capture-group index can silently produce plausible-looking
  wrong names.
- If a dry-run preview shows unexpected matches (wrong files, empty
  results, garbled names), stop and fix the command. Don't apply anyway
  and rely on `--undo` as a substitute for checking first.
- `--undo`/`--redo` operate per-directory on the _last_ batch only. They're
  a safety net for mistakes just made, not a general history browser.
