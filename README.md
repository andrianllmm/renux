# re.name

**A Python command-line tool for bulk file renaming and organization using regex.**

**[Video Demo](https://www.youtube.com/watch?v=dQw4w9WgXcQ)**

## About

`re.name` is a Python-based CLI tool that automates file renaming and organization tasks. It simplifies bulk renaming with features like regex, placeholders (counter, date), and text transformations, making it ideal for situations such as renaming photos, cleaning up download folders, or enforcing consistent naming conventions.

## Features

- **Regex:** Perform advanced renaming with pattern matching, capturing groups, and replacements.
- **Targeted Renaming:** Rename file names, extensions, or both, offering full control over which parts of a file to modify.
- **Case Sensitivity:** Switch between case-sensitive and case-insensitive searches.
- **Counter Placeholders:** Add incremental counters (e.g., file1.txt, file2.txt) with customizable starting points, increments, and padding.
- **Date Placeholders:** Include file creation/modification dates or the current date in your filenames with customizable formats.
- **Text Transformations:** Apply transformations like slugify, capitalize, reverse, and others.
- **Safe Renaming:** Dry-run mode previews changes, checks for duplicate names, and confirms before applying changes.
- **Rich Console Output:** Visual tree views and clear, informative outputs using the `rich` library.

## Design Choices

- **Regex vs Glob**: `re.name` uses regex for file renaming instead of simpler globbing (wildcards like `*` and `?`). Regex allow for complex and precise pattern matching and substitution, such as matching specific parts of filenames, capturing groups, and applying transformations based on conditions.

- **CLI vs GUI**: `re.name` follows a command-line interface (CLI) approach instead of a graphical user interface (GUI). CLI
  allow for faster bulk operations by just using the keyboard once familiarized.

## File Structure

```
re.name/
├── project.py
├── requirements.txt
├── test_project.py
├── README.md
```

- `project.py`: The core script for the renaming logic.
- `test_project.py`: Unit tests to validate the tool’s functionality.
- `requirements.txt`: Lists all the required Python packages.
- `README.md`: Project documentation (this file).

## Installation

1. Clone the repository:

```bash
git clone https://github.com/andrianllmm/re.name.git
cd re.name
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

### Usage

```bash
python project.py [directory] pattern replacement
```

- `[directory]` is where files are located (default is the current directory).
- `pattern` is the search pattern, which can be a regular expression.
- `replacement` is the replacement string for the pattern.

**Options**

- `-c`, `--count`: Max replacements per file (default is 0, meaning unlimited).
- `-s`, `--case-sensitive`: Makes the search case-sensitive (default is false).
- `-r`, `--regex`: Treats the pattern as a regular expression (default is false).
- `--apply-to`: Specifies where the renaming should be applied. Options are:
  - `name`: Rename the file's base name (default).
  - `ext`: Rename the file's extension.
  - `both`: Rename both the name and extension.

**Markup**

- **Text transformations**: `{string|operation}`, e.g. `{hello, world|slugify}` would turn into a slugified version like `hello-world`
- **Counter**: `{counter(start=1,step=1,padding=1)}`, .e.g. `{counter(1,2,3)}` will generate a sequence like `001`, `003`, `005`, etc.
- **Dates**: `{now|created_at|modified_at(<format>)}`, e.g. `{now(%Y)}` will replace it with the current year like 2025.

Run `python project.py -h` for more details.

## Examples

- Rename files starting with "IMG*" to "Image*":

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

## Testing

Run tests with:

```bash
pytest test_project.py
```

The [test](test_project.py) includes a variety of edge cases, feature combinations, and error scenarios.
It uses mocking, which ensures that no files are actually modified during testing.
