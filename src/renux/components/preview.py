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

        renames = get_renames(
            self.app.files,
            self.app.directory,
            self.app.pattern,
            self.app.replacement,
            self.app.options,
        )

        self._tree.root.remove_children()
        for old, new in renames:
            disabled = old in self.app.disabled_files
            text = Text()
            text.append(
                "▢ " if disabled else "▣ ", "dim" if disabled else THEME.primary
            )
            text.append(old, "dim" if disabled else THEME.foreground)
            if old != new:
                text.append(" → ", "dim bold"),
                text.append(new, str("dim" if disabled else THEME.primary) + " bold"),

            self._tree.root.add_leaf(text, data=old)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        file_name = event.node.data
        if file_name in self.app.disabled_files:
            self.app.disabled_files.remove(file_name)
        else:
            self.app.disabled_files.append(file_name)
        self.update_preview()
