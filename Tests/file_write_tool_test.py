import os
import sys
from pathlib import Path
import importlib.util
import pytest
from unittest.mock import patch, mock_open, MagicMock
from pydantic import ValidationError

try:
    from src.code_genereator.tools.file_write_tool import FileWriteTool, FileWriteToolInput
    import src.code_genereator.tools.file_write_tool as file_write_tool_module
except Exception:
    import types

    crewai_module = types.ModuleType("crewai")
    tools_module = types.ModuleType("crewai.tools")

    class BaseTool:
        pass

    tools_module.BaseTool = BaseTool
    crewai_module.tools = tools_module
    sys.modules["crewai"] = crewai_module
    sys.modules["crewai.tools"] = tools_module

    REPO_ROOT = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "file_write_tool_module",
        REPO_ROOT / "src/code_genereator/tools/file_write_tool.py",
    )
    file_write_tool_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(file_write_tool_module)
    FileWriteTool = file_write_tool_module.FileWriteTool
    FileWriteToolInput = file_write_tool_module.FileWriteToolInput


def _compute_base_dir():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(file_write_tool_module.__file__))))
    return base_dir


def test_file_write_tool_happy_path_writes_file_and_creates_directories():
    """Validate successful file write with directory creation and correct return message."""
    tool = FileWriteTool()
    file_path = "dist/backend/main.py"
    content = "print('hello')"
    base_dir = _compute_base_dir()
    full_path = os.path.join(base_dir, file_path)
    parent_dir = os.path.dirname(full_path)

    m_open = mock_open()
    with patch.object(file_write_tool_module.os, "makedirs") as makedirs_mock, \
         patch("builtins.open", m_open):
        result = tool._run(file_path=file_path, content=content)

    assert result == f"Successfully wrote file to: {file_path}"
    makedirs_mock.assert_called_once_with(parent_dir, exist_ok=True)
    m_open.assert_called_once_with(full_path, "w", encoding="utf-8")
    handle = m_open()
    handle.write.assert_called_once_with(content)


def test_file_write_tool_permission_error_returns_message():
    """Ensure PermissionError is caught and returns the proper error message."""
    tool = FileWriteTool()
    file_path = "dist/backend/secret.py"
    content = "data"
    base_dir = _compute_base_dir()
    full_path = os.path.join(base_dir, file_path)
    parent_dir = os.path.dirname(full_path)

    with patch.object(file_write_tool_module.os, "makedirs") as makedirs_mock, \
         patch("builtins.open", side_effect=PermissionError):
        result = tool._run(file_path=file_path, content=content)

    assert result == f"Error: Permission denied when writing to {file_path}"
    makedirs_mock.assert_called_once_with(parent_dir, exist_ok=True)


def test_file_write_tool_generic_exception_returns_message():
    """Ensure generic exceptions are caught and formatted correctly."""
    tool = FileWriteTool()
    file_path = "dist/backend/fail.py"
    content = "data"

    with patch.object(file_write_tool_module.os, "makedirs", side_effect=Exception("boom")):
        result = tool._run(file_path=file_path, content=content)

    assert result == f"Error writing file {file_path}: boom"


def test_file_write_tool_no_parent_dir_skips_makedirs():
    """Verify that when parent_dir is empty, os.makedirs is not called."""
    tool = FileWriteTool()
    file_path = "file.txt"
    content = "plain"

    original_dirname = file_write_tool_module.os.path.dirname
    try:
        file_write_tool_module.os.path.dirname = MagicMock(return_value="")
        m_open = mock_open()
        with patch.object(file_write_tool_module.os, "makedirs") as makedirs_mock, \
             patch("builtins.open", m_open):
            result = tool._run(file_path=file_path, content=content)
    finally:
        file_write_tool_module.os.path.dirname = original_dirname

    assert result == f"Successfully wrote file to: {file_path}"
    makedirs_mock.assert_not_called()
    m_open.assert_called_once_with(file_path, "w", encoding="utf-8")


def test_file_write_tool_input_validation_success():
    """Validate that FileWriteToolInput accepts proper inputs."""
    data = FileWriteToolInput(file_path="dist/app.py", content="print('ok')")
    assert data.file_path == "dist/app.py"
    assert data.content == "print('ok')"


def test_file_write_tool_input_validation_error_missing_fields():
    """Validate that FileWriteToolInput raises ValidationError for missing fields."""
    with pytest.raises(ValidationError):
        FileWriteToolInput()