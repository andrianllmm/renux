DEFAULT_OPTIONS: dict[str, str | int | bool] = {
    "count": 0,
    "regex": True,
    "case_sensitive": False,
    "apply_to": "name",
}

APPLY_TO_LABELS = {
    "Filename only": "name",
    "Extension only": "ext",
    "Filename + Extension": "both",
}
APPLY_TO_OPTIONS = [(label, key) for label, key in APPLY_TO_LABELS.items()]
