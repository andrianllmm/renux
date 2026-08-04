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


def test_headless_undo_reverts_last_rename(tmp_path, monkeypatch):
    """`--undo` should revert the last headless rename without opening the TUI."""
    _make_files(tmp_path, ["foo1.txt", "foo2.txt"])

    monkeypatch.setattr("sys.argv", ["renux", str(tmp_path), "foo", "bar", "--yes"])
    main()
    assert sorted(os.listdir(tmp_path)) == ["bar1.txt", "bar2.txt"]

    monkeypatch.setattr("sys.argv", ["renux", str(tmp_path), "--undo"])
    main()
    assert sorted(os.listdir(tmp_path)) == ["foo1.txt", "foo2.txt"]


def test_headless_redo_reapplies_last_undo(tmp_path, monkeypatch):
    """`--redo` should reapply the last headless undo without opening the TUI."""
    _make_files(tmp_path, ["foo1.txt", "foo2.txt"])

    monkeypatch.setattr("sys.argv", ["renux", str(tmp_path), "foo", "bar", "--yes"])
    main()
    monkeypatch.setattr("sys.argv", ["renux", str(tmp_path), "--undo"])
    main()
    assert sorted(os.listdir(tmp_path)) == ["foo1.txt", "foo2.txt"]

    monkeypatch.setattr("sys.argv", ["renux", str(tmp_path), "--redo"])
    main()
    assert sorted(os.listdir(tmp_path)) == ["bar1.txt", "bar2.txt"]


def test_headless_undo_nothing_to_undo(tmp_path, monkeypatch, capsys):
    """`--undo` with an empty undo stack should report and not error."""
    monkeypatch.setattr("sys.argv", ["renux", str(tmp_path), "--undo"])

    main()

    assert "Nothing to undo." in capsys.readouterr().out


def test_headless_redo_nothing_to_redo(tmp_path, monkeypatch, capsys):
    """`--redo` with an empty redo stack should report and not error."""
    monkeypatch.setattr("sys.argv", ["renux", str(tmp_path), "--redo"])

    main()

    assert "Nothing to redo." in capsys.readouterr().out


def test_headless_exclude_skips_matching_files(tmp_path, monkeypatch):
    """`--exclude` should skip files matching an exact name or glob pattern."""
    _make_files(tmp_path, ["README.md", "Dockerfile", "foo1.txt", "foo2.txt"])

    monkeypatch.setattr(
        "sys.argv",
        [
            "renux",
            str(tmp_path),
            "foo",
            "bar",
            "--yes",
            "--exclude",
            "README.md",
            "--exclude",
            "Dockerfile",
        ],
    )

    main()

    assert sorted(os.listdir(tmp_path)) == [
        "Dockerfile",
        "README.md",
        "bar1.txt",
        "bar2.txt",
    ]
