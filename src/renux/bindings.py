from textual.binding import Binding, BindingType

BINDINGS: list[BindingType] = [
    Binding(
        "ctrl+q",
        "quit",
        "Quit",
        priority=True,
        tooltip="Exit the app",
    ),
    Binding("ctrl+s", "save", "Save", priority=True, tooltip="Apply renaming"),
    Binding(
        "ctrl+l", "clear_form", "Clear", priority=True, tooltip="Clear form values"
    ),
    Binding("ctrl+r", "toggle_regex", "Regex", priority=True, tooltip="Toggle regex"),
]
