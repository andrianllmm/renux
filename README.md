<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/renux.svg?style=flat)](https://pypi.org/project/renux/)
[![Downloads](https://img.shields.io/pypi/dm/renux.svg?style=flat)](https://pypi.org/project/renux/)
[![License](https://img.shields.io/github/license/andrianllmm/renux?style=flat)](https://github.com/andrianllmm/renux/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/andrianllmm/renux?style=flat)](https://github.com/andrianllmm/renux/stargazers)

# renux

**A terminal-based bulk file renamer with a TUI**

<img src="docs/images/preview.gif" alt="Preview" width="500">

</div>

###

## About

`renux` is a tool with a text-based (terminal) user interface (TUI) that
automates file renaming. It simplifies this task with features like regex,
placeholders, and text transformations, making it ideal for situations such as
renaming photos, cleaning up download folders, or enforcing consistent naming
conventions.

### Features

- **Regex**: perform advanced renaming with pattern matching, capturing groups,
  and replacements.
- **Text transformations**: apply text transformations like slugify, camelCase
  to snake_case, and more.
- **Counter placeholders**: add incremental counters (e.g., file1.txt,
  file2.txt) with customizable starting points, increments, and padding.
- **Date placeholders**: include file creation/modification dates or the current
  date in filenames with customizable formats.
- **Backup and undo/redo**: save and restore changes to your files.
- **File exclusion**: exclude files from renaming.
- **Keyboard shortcuts**: use hotkeys to quickly apply actions and navigate the
  UI.

## Installation

Using [pipx](https://pipx.pypa.io/stable/) (recommended).

```sh
pipx install renux
```

Alternatively, you can use [pip](https://pip.pypa.io/en/stable/).

## Usage

```sh
renux [directory] [pattern] [replacement]
```

- `directory`: Directory where files are located (default is the current
  directory or `.`).
- `pattern`: Search pattern, which can be a regular expression (default is '').
- `replacement`: Replacement string for the pattern (default is '').

**Options**

- `-c COUNT`, `--count COUNT`: Max replacements per file (default is 0, meaning
  unlimited).
- `-r`, `--regex`: Treats the pattern as a regular expression (default is True).
- `--case-sensitive`: Makes the search case-sensitive (default is False).
- `--apply-to`: Specifies where the renaming should be applied. Options are:
  - `name`: Rename the file's base name (default).
  - `ext`: Rename the file's extension.
  - `both`: Rename both the name and extension.

**Markup**

- **Text transformations**: `{string|operation}`

  - `slugify`: Convert into a URL/filename-friendly format (e.g., "hello world"
    → "hello-world")
  - `lower`: Convert to lowercase
  - `upper`: Convert to uppercase
  - `caps`: Capitalize the first letter
  - `title`: Capitalize each word
  - `camel`: Convert to camel case (e.g., "hello world" → "helloWorld")
  - `pascal`: Convert to pascal case (e.g., "hello world" → "HelloWorld")
  - `snake`: Convert to snake case (e.g., "hello world" → "hello_world")
  - `kebab`: Convert to kebab case (e.g., "hello world" → "hello-world")
  - `swapcase`: Swap the case (e.g., "Hello World" → "hELLO wORLD")
  - `reverse`: Reverse the string (e.g., "Hello World" → "dlroW olleH")
  - `strip`: Remove leading and trailing whitespace
  - `len`: Get the length of the string

- **Counter**: `{counter(start=1,step=1,padding=1)}`, e.g., `{counter(1,2,3)}`
  will generate a sequence like `001`, `003`, `005`, ...
- **Dates**: `{now|created_at|modified_at(<format>)}`, e.g., `{now(%Y)}` will
  replace it with the current year

Run `python project.py -h` for more details.

### Examples

- Rename files starting with "IMG" to "Image":
  ```sh
  python project.py my_photos/ IMG_ Image_
  ```
- Rename all `.txt` files to `.bak`:
  ```sh
  python project.py my_directory/ .txt .bak --apply-to ext
  ```
- Use regex to retain information from the old name:
  ```sh
  python project.py my_documents "document (\d).pdf" "doc (\1).pdf" -r
  ```
- Append a counter to filenames:
  ```sh
  python project.py my_files/ file "file_{counter}"
  ```
- Append creation year to filenames:
  ```sh
  python project.py my_files/ file "file_{created_at(%Y)}"
  ```
- Apply transformations like slugify:
  ```sh
  python project.py my_files "(.*)" "{filename|slugify}" -r
  ```

## Dev Setup

1. Clone the repo
   ```sh
   git clone https://github.com/andrianllmm/renux.git
   cd renux
   ```
2. Create and activate a virtual environment
   ```sh
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```
3. Install the dependencies
   ```sh
   pip install -r requirements.txt
   ```

### Testing

Run tests with:

```sh
pytest
```

## Contributing

Contributions are welcome! To get started:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## Issues

Found a bug or issue? Report it on the
[issues page](https://github.com/andrianllmm/renux/issues).
