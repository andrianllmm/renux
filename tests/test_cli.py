import os

from renux.cli import main


def _make_files(tmp_path, names):
    for name in names:
        (tmp_path / name).touch()


def test_headless_dry_run_does_not_rename(tmp_path, monkeypatch):
    """`--dry-run` should preview the rename without touching any files."""
    _make_files(tmp_path, ["foo1.txt", "foo2.txt"])

    monkeypatch.setattr("sys.argv", ["renux", str(tmp_path), "foo", "bar", "--dry-run"])

    main()

    assert sorted(os.listdir(tmp_path)) == ["foo1.txt", "foo2.txt"]


def test_headless_yes_applies_rename(tmp_path, monkeypatch):
    """`--yes` should apply the rename immediately without opening the TUI."""
    _make_files(tmp_path, ["foo1.txt", "foo2.txt"])

    monkeypatch.setattr("sys.argv", ["renux", str(tmp_path), "foo", "bar", "--yes"])

    main()

    assert sorted(os.listdir(tmp_path)) == ["bar1.txt", "bar2.txt"]


def test_headless_no_matches(tmp_path, monkeypatch):
    """Headless mode should report and exit cleanly when nothing matches."""
    _make_files(tmp_path, ["baz.txt"])

    monkeypatch.setattr("sys.argv", ["renux", str(tmp_path), "foo", "bar", "--yes"])

    main()

    assert sorted(os.listdir(tmp_path)) == ["baz.txt"]
