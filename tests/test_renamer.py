import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from renux.renamer import (
    apply_renames,
    apply_text_operations,
    get_rename,
    get_renames,
    process_counter_placeholder,
    process_date_placeholders,
)


@pytest.fixture
def mock_os_functions():
    """
    Mock the filesystem-related functions in os to simulate file system operations
    during testing without actually interacting with the filesystem.
    """
    with (
        patch("os.path.isdir", MagicMock()) as mock_isdir,
        patch("os.scandir", MagicMock()) as mock_scandir,
        patch("os.rename", MagicMock()) as mock_rename,
        patch("os.path.exists", MagicMock()) as mock_exists,
        patch("os.path.getctime", MagicMock()) as mock_getctime,
        patch("os.path.getmtime", MagicMock()) as mock_getmtime,
    ):

        # Yield the mocks so the test can access and control their behavior
        yield {
            "isdir": mock_isdir,
            "scandir": mock_scandir,
            "rename": mock_rename,
            "exists": mock_exists,
            "getctime": mock_getctime,
            "getmtime": mock_getmtime,
        }


def test_apply_renames(mock_os_functions):
    """
    Test the `apply_renames` function to ensure the renaming operations
    are applied correctly.
    """
    renames = [
        ("file1.txt", "newfile1.txt"),
        ("file2.txt", "newfile2.txt"),
        ("file3.txt", "newfile3.txt"),
    ]

    apply_renames(
        directory=".",
        renames=renames,
    )

    # Assert that each file was renamed
    mock_rename = mock_os_functions["rename"]
    for old, new in renames:
        mock_rename.assert_any_call(
            os.path.join(".", old),
            os.path.join(".", new),
        )


def test_get_renames():
    """
    Test renaming multiple files at once.
    """
    files = ["file1.txt", "file2.txt", "file3.txt"]
    expected_renames = [
        ("file1.txt", "newfile1.txt"),
        ("file2.txt", "newfile2.txt"),
        ("file3.txt", "newfile3.txt"),
    ]
    pattern = "file"
    replacement = "newfile"

    renames = get_renames(
        files=files,
        directory=".",
        pattern=pattern,
        replacement=replacement,
        options={
            "count": 0,
            "regex": False,
            "case_sensitive": False,
            "apply_to": "name",
        },
    )
    assert renames == expected_renames


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
        options={"count": 0},
    )
    assert result == "new_new.txt"
    # Count = 1
    result = get_rename(
        file_name="file_file.txt",
        directory=".",
        pattern="file",
        replacement="new",
        options={"count": 1},
    )
    assert result == "new_file.txt"

    # Use regex
    result = get_rename(
        file_name="FILE123.txt",
        directory=".",
        pattern=r"\d+",
        replacement="",
        options={"regex": True},
    )
    assert result == "FILE.txt"
    # Group capture and reference
    result = get_rename(
        file_name="file123name.txt",
        directory=".",
        pattern=r"(file)(\d+)(name)",
        replacement=r"\3-\2-\1",
        options={"regex": True},
    )
    assert result == "name-123-file.txt"

    # Case-insensitive
    result = get_rename(
        file_name="FILE1.txt",
        directory=".",
        pattern="file",
        replacement="newfile",
        options={"case_sensitive": False},
    )
    assert result == "newfile1.txt"
    # Case-sensitive
    result = get_rename(
        file_name="FILE1.txt",
        directory=".",
        pattern="file",
        replacement="newfile",
        options={"case_sensitive": True},
    )
    assert result == "FILE1.txt"

    # Apply to extension
    result = get_rename(
        file_name="FILE1.txt",
        directory=".",
        pattern="txt",
        replacement="bat",
        options={"apply_to": "ext"},
    )
    assert result == "FILE1.bat"
    # Apply to both
    result = get_rename(
        file_name="txt.txt",
        directory=".",
        pattern="txt",
        replacement="bat",
        options={"apply_to": "both"},
    )
    assert result == "bat.bat"


@pytest.mark.parametrize(
    "replacement, expected_output",
    [
        ("{file name|slugify}", "file-name"),
        ("{filename|lower}", "filename"),
        ("{filename|upper}", "FILENAME"),
        ("{filename|caps}", "Filename"),
        ("{file name|title}", "File Name"),
        ("{file name|camel}", "fileName"),
        ("{file name|pascal}", "FileName"),
        ("{file name|snake}", "file_name"),
        ("{file name|kebab}", "file-name"),
        ("{fileName|snake}", "file_name"),
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
