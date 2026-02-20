import os
import builtins
from typing import Type
from unittest.mock import MagicMock
import pytest


class FileWriteToolInput:
    def __init__(self, file_path: str, content: str):
        self.file_path = file_path
        self.content = content


class FileWriteTool:
    name: str = "file_write_tool"
    description: str = (
        "Writes content to a file at the specified path. "
        "Use this to save generated code files to the dist/ directory. "
        "The tool will create any necessary parent directories. "
        "Example: file_path='dist/backend/main.py', content='# Python code here'"
    )
    args_schema: Type = FileWriteToolInput

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.base_dir = base_dir

    def _run(self, file_path: str, content: str) -> str:
        try:
            full_path = os.path.join(self.base_dir, file_path)
            parent_dir = os.path.dirname(full_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote file to: {file_path}"
        except PermissionError:
            return f"Error: Permission denied when writing to {file_path}"
        except Exception as e:
            return f"Error writing file {file_path}: {str(e)}"


@pytest.fixture
def tool(tmp_path):
    return FileWriteTool(base_dir=tmp_path)


@pytest.mark.parametrize(
    "relative_path,content",
    [
        ("dist/backend/main.py", "print('hello')"),
        ("dist/empty.txt", ""),
        ("dist/nested/deep/file.txt", "deep content"),
    ],
)
def test_file_write_success_creates_dirs_and_writes_content(tool, tmp_path, relative_path, content):
    """Test that the tool writes content and creates parent directories."""
    result = tool._run(relative_path, content)
    full_path = tmp_path / relative_path
    assert result == f"Successfully wrote file to: {relative_path}"
    assert full_path.exists()
    assert full_path.read_text(encoding="utf-8") == content


def test_file_write_permission_error_returns_message(tool, monkeypatch):
    """Test that PermissionError is handled and returns a clear message."""
    mock_open = MagicMock()
    mock_open.side_effect = PermissionError()
    monkeypatch.setattr(builtins, "open", mock_open)
    result = tool._run("dist/forbidden.txt", "data")
    assert result == "Error: Permission denied when writing to dist/forbidden.txt"


def test_file_write_generic_exception_returns_message(tool, monkeypatch):
    """Test that generic exceptions are caught and returned as error messages."""
    monkeypatch.setattr(os, "makedirs", MagicMock(side_effect=Exception("boom")))
    result = tool._run("dist/error.txt", "content")
    assert result.startswith("Error writing file dist/error.txt: ")
    assert "boom" in result


def test_file_write_with_none_path_returns_error_message(tool):
    """Test that a None file_path results in an error message due to join failure."""
    result = tool._run(None, "content")
    assert result.startswith("Error writing file None:")