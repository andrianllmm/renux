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
    Binding("ctrl+z", "undo", "Undo", priority=True, tooltip="Undo last rename"),
    Binding("ctrl+y", "redo", "Redo", priority=True, tooltip="Redo last undo"),
    Binding(
        "ctrl+l", "clear_form", "Clear", priority=True, tooltip="Clear form values"
    ),
    Binding("ctrl+r", "toggle_regex", "Regex", priority=True, tooltip="Toggle regex"),
]
