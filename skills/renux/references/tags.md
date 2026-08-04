# renux tag & filter reference

Tags go in the `replacement` argument as `{tag}` or `{tag(args)}`. Filters
transform a string value as `{value|filter}`, and can chain:
`{value|filter1|filter2}`.

## Referring to the original filename in the replacement

To reuse part of the matched original name instead of discarding it, capture
it in the regex `pattern` with parentheses and reference it in `replacement`
with `\1`, `\2`, etc. (standard regex backreferences).

- **Backreference only** (no filter): `pattern="(.*)\.pdf"`,
  `replacement="\1_old.pdf"`
- **Backreference + filter** (most common case: converting names to
  snake_case, kebab-case, etc.): wrap the backreference in braces with a
  filter, `{\1|filter}`. Match the whole stem with `(.*)` to transform the
  entire name:
  ```sh
  renux ./files "(.*)" "{\1|slugify}" -r
  ```
  This is the idiomatic way to do whole-name case conversions.

  **Verified pitfall:** a doc example that circulates for renux,
  `renux my_files "(.*)" "{filename|slugify}" -r`, does not do what it
  looks like. `filename` there is not a placeholder that resolves to the
  original name; it's parsed as a literal string, so every file ends up
  renamed to literally `filename.ext`. Confirmed by running it directly:
  `(.*)` + `{filename|slugify}` renames every file to `filename.txt`, while
  `(.*)` + `{\1|slugify}` correctly slugifies each name individually.
  Always use `\N` (a backreference) inside the braces, never a bare word.

## Text-transform filters: `{string|filter}`

| Filter | Effect | Example |
|---|---|---|
| `slugify` | URL/filename-friendly | "hello world" to "hello-world" |
| `lower` | lowercase | |
| `upper` | UPPERCASE | |
| `caps` | Capitalize first letter | |
| `title` | Capitalize Each Word | |
| `camel` | camelCase | "hello world" to "helloWorld" |
| `pascal` | PascalCase | "hello world" to "HelloWorld" |
| `snake` | snake_case | "hello world" to "hello_world" |
| `kebab` | kebab-case | "hello world" to "hello-world" |
| `swapcase` | swap case | "Hello World" to "hELLO wORLD" |
| `reverse` | reverse the string | "Hello World" to "dlroW olleH" |
| `strip` | trim leading/trailing whitespace | |
| `len` | length of the string (numeric) | |

## Placeholders

**Counter**: `{counter(start=1,step=1,padding=1)}`, e.g. `{counter(1,2,3)}`.
Each distinct placeholder occurrence tracks its own sequence, advancing by
`step` after every file. Use `padding` for zero-padded numbers
(`{counter(1,1,3)}` gives 001, 002, 003...).

**Date/time**
- `{now(<format>)}`: current date/time, e.g. `{now(%Y-%m-%d)}`.
- `{created_at(<format>)}`: file creation date/time.
- `{modified_at(<format>)}`: file last-modified date/time.
- Format strings use standard `strftime` directives (`%Y`, `%m`, `%d`, `%H`,
  `%M`, `%S`, ...).

**File**
- `{size(<unit>)}`: file size, auto-scaled to the largest sensible unit
  unless `unit` is given (`b`, `kb`, `mb`, `gb`).

**Image** (EXIF; unavailable for images without EXIF data, e.g. screenshots
or re-exported/edited images. Resolves empty or fails, so warn the user if
they're renaming screenshots with EXIF-only tags)
- `{width}`, `{height}`: pixel dimensions.
- `{taken_at(<format>)}`: capture date/time from EXIF.
- `{camera_make}`, `{camera_model}`: camera manufacturer/model.

**Location** (GPS EXIF, same availability caveat as Image)
- `{latitude}`, `{longitude}`: decimal degrees.
- `{altitude}`: meters.

**Video**
- `{video_width}`, `{video_height}`: pixel dimensions.
- `{frame_rate}`: not available for all containers (e.g. MP4).
- `{duration}`: seconds.

## Worked examples

All of these were run and verified against a real `renux` install
(`--dry-run`).

- Prefix today's date onto every file. Pattern is `^`, not `""`; an empty
  pattern is a no-op in renux, it aborts before matching:
  ```sh
  renux ./inbox "^" "{now(%Y-%m-%d)}_" -y
  ```
- Number files sequentially with zero-padding, keeping extension:
  ```sh
  renux ./photos "(.*)\.(jpg|jpeg|png)" "photo_{counter(1,1,3)}.\2" -r -y
  ```
- Rename photos using their EXIF capture date:
  ```sh
  renux ./photos "(.*)" "{taken_at(%Y%m%d)}_\1" -r -y
  ```
- Append file size:
  ```sh
  renux ./downloads "$" "_{size(mb)}" -y
  ```
- Whole-name case conversion (slugify all names):
  ```sh
  renux ./docs "(.*)" "{\1|slugify}" -r -y
  ```
- Swap extension `.txt` to `.md`. With `--apply-to ext`, the pattern matches
  against the extension without its leading dot, `"txt"` not `".txt"` (a
  leading `.` in the pattern needs an extra character before "txt" to
  match):
  ```sh
  renux ./notes "txt" "md" --apply-to ext -y
  ```

If a request needs a tag/filter not listed here, check the live source of
truth before guessing: run `renux --help`, or if working inside the renux
repo itself, read `src/renux/tags.py` (the README docs are generated from
this registry).
