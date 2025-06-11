import os
from typing import TYPE_CHECKING
from rich.text import Text
from textual.widget import Widget
from textual.widgets import Tree

from renux.renamer import get_renames
from renux.ui import THEME

if TYPE_CHECKING:
    from renux.app import RenameApp


class Preview(Widget):
    """Tree widget for live preview of renaming changes."""

    app: "RenameApp"

    def compose(self):
        tree = Tree(self.app.directory, id="preview-tree")
        yield tree

    def on_mount(self) -> None:
        self._tree: Tree = self.query_one("#preview-tree", Tree)
        self._tree.root.expand()
        self.update_preview()

    def update_preview(self) -> None:
        # Get files and their renaming results
        files = [
            entry.name for entry in os.scandir(self.app.directory) if entry.is_file()
        ]
        renames = get_renames(
            files,
            self.app.directory,
            self.app.pattern,
            self.app.replacement,
            self.app.options,
        )

        self._tree.root.remove_children()
        for old, new in renames:
            if old != new:
                text = Text.assemble(
                    (old, "dim"),
                    (" → ", str(THEME.foreground)),
                    (new, str(THEME.primary)),
                )
            else:
                text = Text(old, style="dim")
            self._tree.root.add(text)
        self._tree.refresh()
