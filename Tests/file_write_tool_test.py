import sys
import types
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch
import pytest
from pydantic import ValidationError

# TEST PLAN
# 1. _run writes content to a file and returns success for non-empty and empty content.
# 2. _run skips directory creation when parent directory is empty.
# 3. _run handles PermissionError with a specific message.
# 4. _run handles generic exceptions and reports the error.
# 5. FileWriteToolInput validates required fields.
# 6. Tool metadata exposes name, description, and args_schema.

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _ensure_crewai():
    if "crewai" not in sys.modules:
        crewai = types.ModuleType("crewai")
        tools = types.ModuleType("crewai.tools")

        class BaseTool:
            pass

        tools.BaseTool = BaseTool
        crewai.tools = tools
        sys.modules["crewai"] = crewai
        sys.modules["crewai.tools"] = tools


_ensure_crewai()
try:
    from code_genereator.tools.file_write_tool import FileWriteTool, FileWriteToolInput
    module = sys.modules["code_genereator.tools.file_write_tool"]
except Exception:
    _ensure_crewai()
    spec = importlib.util.spec_from_file_location(
        "module_under_test",
        REPO_ROOT / "src/code_genereator/tools/file_write_tool.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    FileWriteTool = module.FileWriteTool
    FileWriteToolInput = module.FileWriteToolInput


@pytest.fixture
def tool_instance():
    """Provides a FileWriteTool instance for tests."""
    try:
        return FileWriteTool()
    except Exception:
        return FileWriteTool  # fallback if FileWriteTool is an instance-like object


def _get_tool_attr(tool_cls, attr):
    if hasattr(tool_cls, attr):
        return getattr(tool_cls, attr)
    if hasattr(tool_cls, "model_fields") and attr in tool_cls.model_fields:
        field = tool_cls.model_fields[attr]
        if field.default is not None:
            return field.default
    try:
        inst = tool_cls()
        if hasattr(inst, attr):
            return getattr(inst, attr)
    except Exception:
        pass
    if hasattr(tool_cls, "model_fields") and attr in tool_cls.model_fields:
        field = tool_cls.model_fields[attr]
        if field.default is not None:
            return field.default
    return None


@pytest.mark.parametrize("content", ["print('hello')", ""])
def test_run_writes_file_successfully(tmp_path, monkeypatch, tool_instance, content):
    """Validates that _run writes file content and returns success message."""
    fake_file = tmp_path / "a" / "b" / "c" / "d.py"
    monkeypatch.setattr(module, "__file__", str(fake_file))
    result = tool_instance._run("dist/output.txt", content)
    expected_path = tmp_path / "dist" / "output.txt"
    assert expected_path.exists()
    assert expected_path.read_text(encoding="utf-8") == content
    assert result == "Successfully wrote file to: dist/output.txt"


def test_run_skips_makedirs_when_parent_dir_empty(tool_instance):
    """Ensures no directories are created when parent_dir is empty."""
    m_open = mock_open()
    with patch.object(module.os.path, "dirname", return_value=""), \
         patch.object(module.os, "makedirs") as m_makedirs, \
         patch("builtins.open", m_open):
        result = tool_instance._run("file.txt", "data")
    m_makedirs.assert_not_called()
    m_open.assert_called_once_with("file.txt", "w", encoding="utf-8")
    assert result == "Successfully wrote file to: file.txt"


def test_run_permission_error_returns_message(tool_instance):
    """Checks that PermissionError is handled gracefully with a specific message."""
    with patch.object(module.os, "makedirs") as m_makedirs, \
         patch("builtins.open", side_effect=PermissionError):
        result = tool_instance._run("dist/secret.txt", "secret")
    assert m_makedirs.called
    assert result == "Error: Permission denied when writing to dist/secret.txt"


def test_run_generic_exception_returns_message(tool_instance):
    """Validates that unexpected exceptions return an error description."""
    with patch.object(module.os, "makedirs", side_effect=Exception("boom")), \
         patch("builtins.open", MagicMock()) as m_open:
        result = tool_instance._run("dist/bad.txt", "data")
    assert not m_open.called
    assert result == "Error writing file dist/bad.txt: boom"


def test_input_schema_validation_and_fields():
    """Ensures FileWriteToolInput validates fields and exposes values."""
    model = FileWriteToolInput(file_path="dist/main.py", content="code")
    assert model.file_path == "dist/main.py"
    assert model.content == "code"
    with pytest.raises(ValidationError):
        FileWriteToolInput(file_path="dist/main.py")


def test_tool_metadata():
    """Verifies tool metadata attributes are correctly defined."""
    name = _get_tool_attr(FileWriteTool, "name")
    description = _get_tool_attr(FileWriteTool, "description")
    args_schema = _get_tool_attr(FileWriteTool, "args_schema")
    assert name == "file_write_tool"
    assert description and "Writes content to a file" in description
    assert args_schema is FileWriteToolInput or args_schema == FileWriteToolInput