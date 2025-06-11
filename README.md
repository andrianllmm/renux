# renux
**Bulk file renaming with a terminal UI**

## About

`renux` is a tool with terminal user interface (TUI) that automates file renaming. It simplifies this task with features like regex, placeholders, and text transformations, making it ideal for situations such as renaming photos, cleaning up download folders, or enforcing consistent naming conventions.


## Features

- **Regex**: perform advanced renaming with pattern matching, capturing groups, and replacements.
- **Text transformations**: apply text transformations like slugify, camelCase to snake_case, and more.
- **Counter placeholders**: add incremental counters (e.g., file1.txt, file2.txt) with customizable starting points, increments, and padding.
- **Date placeholders**: include file creation/modification dates or the current date in filenames with customizable formats.
- **Backup and undo/redo**: save and restore changes to your files.
- **File exclusion**: exclude files from renaming.
- **Keyboard shortcuts**: use hotkeys to quickly apply actions and navigate the UI.


## Installation

```bash
pipx install renux
```

## Usage

```bash
renux [directory] [pattern] [replacement]
```

- `[directory]`: Directory where files are located (default is the current directory).
- `pattern`: Search pattern, which can be a regular expression (default is '').
- `replacement`: Replacement string for the pattern (default is '').

**Options**

- `-c`, `--count`: Max replacements per file (default is 0, meaning unlimited).
- `-r`, `--regex`: Treats the pattern as a regular expression (default is False).
- `-s`, `--case-sensitive`: Makes the search case-sensitive (default is False).
- `--apply-to`: Specifies where the renaming should be applied. Options are:
  - `name`: Rename the file's base name (default).
  - `ext`: Rename the file's extension.
  - `both`: Rename both the name and extension.

**Markup**

- **Text transformations**: `{string|operation}`
  - `slugify`: Convert into a URL/filename-friendly format (e.g., "hello world" -> "hello-world")
  - `lower`: Convert to lowercase
  - `upper`: Convert to uppercase
  - `caps`: Capitalize the first letter
  - `title`: Capitalize each word
  - `camel`: Convert to camel case (e.g., "hello world" -> "helloWorld")
  - `pascal`: Convert to pascal case (e.g., "hello world" -> "HelloWorld")
  - `snake`: Convert to snake case (e.g., "hello world" -> "hello_world")
  - `kebab`: Convert to kebab case (e.g., "hello world" -> "hello-world")
  - `swapcase`: Swap the case (e.g., "Hello World" -> "hELLO wORLD")
  - `reverse`: Reverse the string (e.g., "Hello World" -> "dlroW olleH")
  - `strip`: Remove leading and trailing whitespace
  - `len`: Get the length of the string

- **Counter**: `{counter(start=1,step=1,padding=1)}`, .e.g. `{counter(1,2,3)}` will generate a sequence like `001`, `003`, `005`, ...
- **Dates**: `{now|created_at|modified_at(<format>)}`, e.g. `{now(%Y)}` will replace it with the current year

Run `python project.py -h` for more details.

## Examples

- Rename files starting with "IMG" to "Image":

  ```bash
  python project.py my_photos/ IMG_ Image_
  ```

- Rename all `.txt` files to `.bak`:

  ```bash
  python project.py my_directory/ .txt .bak --apply-to ext
  ```

- Use regex to retain information from the old name:

  ```bash
  python project.py my_documents "document (\d).pdf" "doc (\1).pdf" -r
  ```

- Append a counter to filenames:

  ```bash
  python project.py my_files/ file "file_{counter}"
  ```

- Append creation year to filenames:

  ```bash
  python project.py my_files/ file "file_{created_at(%Y)}"
  ```

- Apply transformations like slugify:

  ```bash
  python project.py my_files "(.*)" "{filename|slugify}" -r
  ```


## Development

### Setup

1. Clone the repository:

```bash
git clone https://github.com/andrianllmm/renux.git
cd renux
```

2. Create and activate virtual environment:

```bash
python -m venv venv

# Linux/macOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Testing

Run tests with:

```bash
pytest test_project.py
```

The [test](test_project.py) includes a variety of edge cases, feature combinations, and error scenarios.
It uses mocking, which ensures that no files are actually modified during testing.
