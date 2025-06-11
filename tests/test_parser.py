from renux.parser import parse_args


def test_get_argparser(monkeypatch):
    """
    Test the `get_argparser` function to ensure the command-line arguments
    are parsed correctly.
    """
    directory = "test_dir"
    pattern = "test_pattern"
    replacement = "test_replacement"
    options = {
        "count": 3,
        "regex": True,
        "case_sensitive": True,
        "apply_to": "ext",
    }

    input_args = [
        "project.py",
        directory,
        pattern,
        replacement,
        "--count",
        str(options["count"]),
        "--apply-to",
        options["apply_to"],
    ]
    if options["regex"]:
        input_args.append("--regex")
    if options["case_sensitive"]:
        input_args.append("--case-sensitive")

    monkeypatch.setattr("sys.argv", input_args)

    args = parse_args()

    assert args.directory == directory
    assert args.pattern == pattern
    assert args.replacement == replacement
    assert args.count == options["count"]
    assert args.regex == options["regex"]
    assert args.case_sensitive == options["case_sensitive"]
    assert args.apply_to == options["apply_to"]
