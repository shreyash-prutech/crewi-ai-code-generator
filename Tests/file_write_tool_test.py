import os
import sys
import types
from pathlib import Path
import importlib.util
from unittest.mock import MagicMock, patch, mock_open

import pytest
from pydantic import ValidationError

# Ensure crewai.tools.BaseTool exists for import
if "crewai" not in sys.modules:
    crewai_module = types.ModuleType("crewai")
    tools_module = types.ModuleType("crewai.tools")

    class BaseTool:
        pass

    tools_module.BaseTool = BaseTool
    crewai_module.tools = tools_module
    sys.modules["crewai"] = crewai_module
    sys.modules["crewai.tools"] = tools_module

try:
    from code_genereator.tools.file_write_tool import FileWriteTool, FileWriteToolInput
    import code_genereator.tools.file_write_tool as file_write_tool_module
except Exception:
    REPO_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location(
        "file_write_tool_module", REPO_ROOT / "src/code_genereator/tools/file_write_tool.py"
    )
    file_write_tool_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(file_write_tool_module)
    FileWriteTool = file_write_tool_module.FileWriteTool
    FileWriteToolInput = file_write_tool_module.FileWriteToolInput


@pytest.fixture
def tool_instance():
    """Provide a fresh FileWriteTool instance for tests."""
    return FileWriteTool()


def compute_base_dir():
    """Compute base directory as done by FileWriteTool."""
    return os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(file_write_tool_module.__file__)
            )
        )
    )


def test_file_write_tool_input_validates_fields():
    """Validate that FileWriteToolInput accepts valid data."""
    schema = FileWriteToolInput(file_path="dist/backend/main.py", content="print('hi')")
    assert schema.file_path == "dist/backend/main.py"
    assert schema.content == "print('hi')"


def test_file_write_tool_input_missing_fields_raises():
    """Validate that FileWriteToolInput enforces required fields."""
    with pytest.raises(ValidationError):
        FileWriteToolInput(file_path="dist/backend/main.py")
    with pytest.raises(ValidationError):
        FileWriteToolInput(content="print('hi')")


def test_file_write_tool_class_attributes():
    """Ensure tool metadata attributes are correctly defined."""
    assert FileWriteTool.name == "file_write_tool"
    assert "Writes content to a file" in FileWriteTool.description
    assert FileWriteTool.args_schema is FileWriteToolInput


def test_run_success_creates_dirs_and_writes_file(tool_instance):
    """Test successful write creates parent directories and writes content."""
    file_path = "dist/backend/main.py"
    content = "print('hello')"
    base_dir = compute_base_dir()
    full_path = os.path.join(base_dir, file_path)
    parent_dir = os.path.dirname(full_path)

    m_open = mock_open()
    with patch("builtins.open", m_open), patch.object(file_write_tool_module.os, "makedirs") as m_makedirs:
        result = tool_instance._run(file_path=file_path, content=content)

    m_makedirs.assert_called_once_with(parent_dir, exist_ok=True)
    m_open.assert_called_once_with(full_path, "w", encoding="utf-8")
    m_open().write.assert_called_once_with(content)
    assert result == f"Successfully wrote file to: {file_path}"


def test_run_permission_error_returns_message(tool_instance):
    """Test PermissionError handling returns a specific error message."""
    file_path = "dist/forbidden.py"
    content = "data"

    with patch.object(file_write_tool_module.os, "makedirs") as m_makedirs:
        with patch("builtins.open", side_effect=PermissionError):
            result = tool_instance._run(file_path=file_path, content=content)

    assert m_makedirs.called
    assert result == f"Error: Permission denied when writing to {file_path}"


def test_run_generic_exception_returns_message(tool_instance):
    """Test generic exception handling returns an error message."""
    file_path = "dist/error.py"
    content = "oops"

    with patch.object(file_write_tool_module.os, "makedirs", side_effect=Exception("boom")) as m_makedirs:
        with patch("builtins.open", mock_open()) as m_open:
            result = tool_instance._run(file_path=file_path, content=content)

    assert m_makedirs.called
    assert not m_open.called
    assert result == f"Error writing file {file_path}: boom"


def test_run_skips_makedirs_when_parent_dir_empty(tool_instance):
    """Test that makedirs is skipped when parent_dir is empty."""
    file_path = "simple.txt"
    content = "simple"
    base_dir = compute_base_dir()
    full_path = os.path.join(base_dir, file_path)
    real_dirname = file_write_tool_module.os.path.dirname

    def fake_dirname(path):
        if path == full_path:
            return ""
        return real_dirname(path)

    m_open = mock_open()
    with patch.object(file_write_tool_module.os.path, "dirname", side_effect=fake_dirname) as m_dirname, \
         patch.object(file_write_tool_module.os, "makedirs") as m_makedirs, \
         patch("builtins.open", m_open):
        result = tool_instance._run(file_path=file_path, content=content)

    assert m_dirname.called
    m_makedirs.assert_not_called()
    m_open.assert_called_once_with(full_path, "w", encoding="utf-8")
    m_open().write.assert_called_once_with(content)
    assert result == f"Successfully wrote file to: {file_path}"