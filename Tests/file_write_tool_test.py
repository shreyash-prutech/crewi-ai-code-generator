import os
import sys
import types
from pathlib import Path
import importlib.util
import pytest
from unittest.mock import patch

# TEST PLAN
# 1. Validate tool has expected metadata and schema definitions
# 2. Ensure input schema raises validation errors for missing/invalid fields
# 3. Verify _run writes content and creates necessary parent directories
# 4. Verify PermissionError during file open is handled gracefully
# 5. Verify PermissionError during directory creation is handled gracefully
# 6. Verify generic exceptions are captured and included in return message

if "crewai" not in sys.modules:
    crewai_module = types.ModuleType("crewai")
    tools_module = types.ModuleType("crewai.tools")

    class DummyBaseTool:
        pass

    tools_module.BaseTool = DummyBaseTool
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
        "file_write_tool_module",
        REPO_ROOT / "src/code_genereator/tools/file_write_tool.py",
    )
    file_write_tool_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(file_write_tool_module)
    FileWriteTool = file_write_tool_module.FileWriteTool
    FileWriteToolInput = file_write_tool_module.FileWriteToolInput


@pytest.fixture
def tool_and_base(tmp_path, monkeypatch):
    fake_file = tmp_path / "a/b/c/d/file.py"
    fake_file.parent.mkdir(parents=True)
    monkeypatch.setattr(file_write_tool_module, "__file__", str(fake_file))
    base_dir = tmp_path / "a"
    return FileWriteTool(), base_dir


def _get_field_descriptions():
    if hasattr(FileWriteToolInput, "__fields__"):
        fields = FileWriteToolInput.__fields__
    else:
        fields = FileWriteToolInput.model_fields
    descriptions = {}
    for name, field in fields.items():
        desc = getattr(field, "description", None)
        if desc is None and hasattr(field, "field_info"):
            desc = getattr(field.field_info, "description", None)
        descriptions[name] = desc
    return descriptions


def test_tool_attributes_and_schema():
    """Validate that tool has expected metadata and schema definitions."""
    tool = FileWriteTool()
    assert tool.name == "file_write_tool"
    assert "Writes content to a file" in tool.description
    assert tool.args_schema is FileWriteToolInput
    field_descriptions = _get_field_descriptions()
    assert "relative path" in field_descriptions["file_path"]
    assert "content to write" in field_descriptions["content"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"content": "x"},
        {"file_path": "path"},
        {"file_path": None, "content": "x"},
        {"file_path": "path", "content": None},
    ],
)
def test_input_schema_validation_errors(kwargs):
    """Ensure input schema raises validation errors for missing/invalid fields."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        FileWriteToolInput(**kwargs)


def test_run_successfully_writes_file_and_creates_directories(tool_and_base):
    """Verify _run writes content and creates necessary parent directories."""
    tool, base_dir = tool_and_base
    file_path = "dist/backend/main.py"
    content = "print('hello')"
    full_path = base_dir / file_path
    with patch.object(file_write_tool_module.os, "makedirs", wraps=os.makedirs) as makedirs:
        result = tool._run(file_path=file_path, content=content)
    assert result == f"Successfully wrote file to: {file_path}"
    assert full_path.exists()
    assert full_path.read_text(encoding="utf-8") == content
    assert makedirs.called
    called_args = makedirs.call_args.args[0]
    assert os.path.commonpath([called_args, str(full_path.parent)]) == os.path.commonpath(
        [str(full_path.parent), called_args]
    )


def test_run_permission_error_on_open_returns_message(tool_and_base):
    """Verify PermissionError during file open is handled gracefully."""
    tool, _ = tool_and_base
    file_path = "dist/backend/main.py"
    with patch("builtins.open", side_effect=PermissionError):
        result = tool._run(file_path=file_path, content="data")
    assert result == f"Error: Permission denied when writing to {file_path}"


def test_run_permission_error_on_makedirs_returns_message(tool_and_base):
    """Verify PermissionError during directory creation is handled gracefully."""
    tool, _ = tool_and_base
    file_path = "dist/backend/main.py"
    with patch.object(file_write_tool_module.os, "makedirs", side_effect=PermissionError):
        result = tool._run(file_path=file_path, content="data")
    assert result == f"Error: Permission denied when writing to {file_path}"


def test_run_generic_exception_returns_message(tool_and_base):
    """Verify generic exceptions are captured and included in return message."""
    tool, _ = tool_and_base
    file_path = "dist/backend/main.py"
    with patch("builtins.open", side_effect=Exception("boom")):
        result = tool._run(file_path=file_path, content="data")
    assert result == f"Error writing file {file_path}: boom"