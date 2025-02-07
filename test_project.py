import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from project import (
    rename_files,
    get_rename,
    apply_text_operations,
    process_counter_placeholder,
    process_date_placeholders,
    parse_arguments,
)


@pytest.fixture
def mock_os_functions():
    """
    Mock the filesystem-related functions in os to simulate file system operations
    during testing without actually interacting with the filesystem.
    """
    with patch("os.path.isdir", MagicMock()) as mock_isdir, patch(
        "os.scandir", MagicMock()
    ) as mock_scandir, patch("os.rename", MagicMock()) as mock_rename, patch(
        "os.path.exists", MagicMock()
    ) as mock_exists, patch(
        "os.path.getctime", MagicMock()
    ) as mock_getctime, patch(
        "os.path.getmtime", MagicMock()
    ) as mock_getmtime:
        yield {
            "isdir": mock_isdir,
            "scandir": mock_scandir,
            "rename": mock_rename,
            "exists": mock_exists,
            "getctime": mock_getctime,
            "getmtime": mock_getmtime,
        }


def test_rename_files_multiple(mock_os_functions):
    """
    Test renaming multiple files at once.
    """
    mock_isdir = mock_os_functions["isdir"]
    mock_scandir = mock_os_functions["scandir"]
    mock_rename = mock_os_functions["rename"]
    mock_exists = mock_os_functions["exists"]

    mock_isdir.return_value = True
    mock_scandir.return_value = [
        MagicMock(is_file=MagicMock(return_value=True), name="file1.txt"),
        MagicMock(is_file=MagicMock(return_value=True), name="file2.txt"),
        MagicMock(is_file=MagicMock(return_value=True), name="file3.txt"),
    ]
    mock_exists.return_value = False

    # Mock user confirmation prompt
    with patch("rich.prompt.Confirm.ask", return_value=True):
        files = ["file1.txt", "file2.txt", "file3.txt"]
        rename_files(
            files=files,
            directory=".",
            pattern="file",
            replacement="newfile",
            count=0,
            case_sensitive=False,
            use_regex=False,
            apply_to="name",
        )

        # Assert that the rename operation was called for each file
        mock_rename.assert_any_call(
            os.path.join(".", "file1.txt"),
            os.path.join(".", "newfile1.txt"),
        )
        mock_rename.assert_any_call(
            os.path.join(".", "file2.txt"),
            os.path.join(".", "newfile2.txt"),
        )
        mock_rename.assert_any_call(
            os.path.join(".", "file3.txt"),
            os.path.join(".", "newfile3.txt"),
        )


def test_get_rename():
    """
    Test the `get_rename` function to ensure it generates
    the correct new filename based on the input parameters.
    """
    # Count = 0
    result = get_rename(
        file_name="file_file.txt",
        directory=".",
        pattern="file",
        replacement="new",
        count=0,
    )
    assert result == "new_new.txt"
    # Count = 1
    result = get_rename(
        file_name="file_file.txt",
        directory=".",
        pattern="file",
        replacement="new",
        count=1,
    )
    assert result == "new_file.txt"

    # Case-insensitive
    result = get_rename(
        file_name="FILE1.txt",
        directory=".",
        pattern="file",
        replacement="newfile",
        case_sensitive=False,
    )
    assert result == "newfile1.txt"
    # Case-sensitive
    result = get_rename(
        file_name="FILE1.txt",
        directory=".",
        pattern="file",
        replacement="newfile",
        case_sensitive=True,
    )
    assert result == "FILE1.txt"

    # Use regex
    result = get_rename(
        file_name="FILE1.txt",
        directory=".",
        pattern=r"\d+",
        replacement="",
        use_regex=True,
    )
    assert result == "FILE.txt"

    # Apply to extension
    result = get_rename(
        file_name="FILE1.txt",
        directory=".",
        pattern="txt",
        replacement="bat",
        apply_to="ext",
    )
    assert result == "FILE1.bat"


@pytest.mark.parametrize(
    "replacement, expected_output",
    [
        ("{file name|slugify}", "file-name"),
        ("{filename|upper}", "FILENAME"),
        ("{filename|lower}", "filename"),
        ("{file name|title}", "File Name"),
        ("{filename|capitalize}", "Filename"),
        ("{FileName|swapcase}", "fILEnAME"),
        ("{filename|reverse}", "emanelif"),
        ("{  filename  |strip}", "filename"),
        ("{filename|len}", "8"),
        ("{filename|invalid}", "filename"),
    ],
)
def test_apply_text_operations(replacement, expected_output):
    """
    Test the `apply_text_operations` function to ensure that
    text transformations are applied correctly.
    """
    result = apply_text_operations(replacement)
    assert result == expected_output


def test_process_counter_placeholder():
    """
    Test the `process_counter_placeholder` function to ensure
    the counter placeholders are replaced with the correct incremented value.
    """
    counters = [1, 2]
    result = process_counter_placeholder(
        "file_{counter}_{counter(1, 2, 3)}.txt", counters
    )
    assert result == "file_1_002.txt"
    assert counters == [2, 4]  # Counters should be incremented accordingly

    # For file names with no counter markup
    result2 = process_counter_placeholder("file_no_counter.txt", counters)
    assert result2 == "file_no_counter.txt"
    assert counters == [2, 4]


def test_process_date_placeholders(mock_os_functions):
    """
    Test the `process_date_placeholders` function to ensure the correct date values
    are inserted for placeholders like {created_at}, {modified_at}, and {now}.
    """
    # Extract mock functions from fixture
    mock_getctime = mock_os_functions["getctime"]
    mock_getmtime = mock_os_functions["getmtime"]

    # Set mock creation and modification times
    mock_getctime.return_value = 1577836800  # Jan 1, 2020
    mock_getmtime.return_value = 1609459200  # Jan 1, 2021

    # Test for created_at placeholder
    result = process_date_placeholders("{created_at(%Y-%m-%d)}", "file1.txt", ".")
    assert result == "2020-01-01"

    # Test for modified_at placeholder
    result = process_date_placeholders("{modified_at(%Y-%m-%d)}", "file1.txt", ".")
    assert result == "2021-01-01"

    # Test for current date (now)
    current_date = datetime.now().strftime("%Y-%m-%d")
    result = process_date_placeholders("{now(%Y-%m-%d)}", "file1.txt", ".")
    assert result == current_date


def test_parse_arguments(monkeypatch):
    """
    Test the `parse_arguments` function to ensure the command-line arguments
    are parsed correctly with default values.
    """
    monkeypatch.setattr(
        "sys.argv", ["program.py", "test_dir", "pattern", "replacement"]
    )

    args = parse_arguments()
    assert args.directory == "test_dir"
    assert args.pattern == "pattern"
    assert args.replacement == "replacement"
    assert args.count == 0
    assert not args.case_sensitive
    assert not args.regex
    assert args.apply_to == "name"


def test_parse_arguments_with_flags(monkeypatch):
    """
    Test the `parse_arguments` function to ensure that flags
    are correctly parsed from the command-line arguments.
    """
    monkeypatch.setattr(
        "sys.argv",
        [
            "program.py",
            "test_dir",
            "pattern",
            "replacement",
            "-c",
            "5",
            "-s",
            "-r",
            "--apply-to",
            "both",
        ],
    )

    args = parse_arguments()
    assert args.count == 5
    assert args.case_sensitive
    assert args.regex
    assert args.apply_to == "both"
