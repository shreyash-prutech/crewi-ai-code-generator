import os
import sys
import types
import importlib.util
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import pytest
from pydantic import ValidationError


def _load_module():
    try:
        from code_genereator.tools import file_write_tool as module
        return module
    except Exception:
        if "crewai" not in sys.modules:
            crewai = types.ModuleType("crewai")
            tools = types.ModuleType("crewai.tools")

            class BaseTool:
                pass

            tools.BaseTool = BaseTool
            crewai.tools = tools
            sys.modules["crewai"] = crewai
            sys.modules["crewai.tools"] = tools
        repo_root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location(
            "file_write_tool", repo_root / "src/code_genereator/tools/file_write_tool.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


@pytest.fixture(scope="module")
def module_under_test():
    return _load_module()


@pytest.fixture
def tool(module_under_test):
    return module_under_test.FileWriteTool()


def _compute_base_dir(module_under_test):
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(module_under_test.__file__)))
    )


def test_write_file_success(tool, module_under_test):
    """Validate successful file write returns success message and uses correct path."""
    base_dir = _compute_base_dir(module_under_test)
    file_path = "dist/backend/main.py"
    content = "print('hello')"
    full_path = os.path.join(base_dir, file_path)
    parent_dir = os.path.dirname(full_path)

    m_open = mock_open()
    with patch("builtins.open", m_open), patch.object(
        module_under_test.os, "makedirs", MagicMock()
    ) as m_makedirs:
        result = tool._run(file_path=file_path, content=content)

    assert result == f"Successfully wrote file to: {file_path}"
    m_makedirs.assert_called_once_with(parent_dir, exist_ok=True)
    m_open.assert_called_once_with(full_path, "w", encoding="utf-8")
    handle = m_open()
    handle.write.assert_called_once_with(content)


@pytest.mark.parametrize(
    "file_path,content",
    [
        ("dist/empty.txt", ""),
        ("", "content for base dir"),
    ],
)
def test_write_file_edge_cases(tool, module_under_test, file_path, content):
    """Validate edge cases with empty content or empty file path."""
    base_dir = _compute_base_dir(module_under_test)
    full_path = os.path.join(base_dir, file_path)
    parent_dir = os.path.dirname(full_path)

    m_open = mock_open()
    with patch("builtins.open", m_open), patch.object(
        module_under_test.os, "makedirs", MagicMock()
    ) as m_makedirs:
        result = tool._run(file_path=file_path, content=content)

    assert result == f"Successfully wrote file to: {file_path}"
    m_makedirs.assert_called_once_with(parent_dir, exist_ok=True)
    m_open.assert_called_once_with(full_path, "w", encoding="utf-8")
    m_open().write.assert_called_once_with(content)


def test_write_file_permission_error(tool, module_under_test):
    """Validate PermissionError is handled with a friendly message."""
    file_path = "dist/secure.txt"
    content = "secure data"

    with patch("builtins.open", side_effect=PermissionError), patch.object(
        module_under_test.os, "makedirs", MagicMock()
    ):
        result = tool._run(file_path=file_path, content=content)

    assert result == f"Error: Permission denied when writing to {file_path}"


def test_write_file_unexpected_error(tool, module_under_test):
    """Validate generic exceptions are returned as error messages."""
    file_path = "dist/boom.txt"
    content = "boom"

    with patch.object(module_under_test.os, "makedirs", side_effect=Exception("boom")):
        result = tool._run(file_path=file_path, content=content)

    assert "Error writing file dist/boom.txt: boom" == result


def test_input_schema_validation_errors(module_under_test):
    """Validate pydantic schema enforces required fields."""
    with pytest.raises(ValidationError):
        module_under_test.FileWriteToolInput(file_path=None, content="x")
    with pytest.raises(ValidationError):
        module_under_test.FileWriteToolInput(file_path="a", content=None)