"""Test the utility functions in the src.utilities module."""
import os
from unittest.mock import mock_open, patch

from src.utilities.util_functions import create_frontend_feedback_story


def test_create_frontend_feedback_story() -> None:
    """Test the creation of the frontend feedback story file."""
    # Given
    # Mock the path to the frontend feedback story file
    frontend_feedback_story_path = os.path.join("/mock/work/dir", ".clean_coder", "frontend_feedback_story.txt")
    # Mock the storyfile_template content
    with patch("os.path.exists", return_value=False), \
        patch("builtins.open", mock_open()) as mock_file, \
        patch("builtins.input", return_value=""), \
        patch("src.utilities.util_functions.Work.dir", return_value="/mock/work/dir"):
        # When
        create_frontend_feedback_story()
        # Then
        mock_file.assert_called_once_with(frontend_feedback_story_path, "w")
        mock_file().write.assert_called_once_with("""<This is the story of your project for a frontend feedback agent. Modify it according to commentaries provided in <> brackets.>""")
