from unittest.mock import MagicMock, patch

from renux.app import RenameApp


@patch("renux.app.get_renames")
@patch("renux.app.apply_renames")
def test_action_save_success(mock_apply, mock_get):
    app = RenameApp(".", "foo", "bar", {})
    app.query_one = MagicMock()
    app.query_one.return_value = MagicMock()

    mock_get.return_value = [("file1.txt", "file2.txt")]

    app.action_save()

    mock_apply.assert_called_once()
    app.query_one.assert_called()
