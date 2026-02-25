import sys
from pathlib import Path
import importlib
import importlib.util
import pytest
from pydantic import ValidationError


def _import_module():
    try:
        return importlib.import_module("code_genereator.tools.custom_tool")
    except Exception:
        # Fallback to file-based import with stubbing crewai.tools.BaseTool if needed
        if "crewai" not in sys.modules:
            crewai_module = importlib.util.module_from_spec(importlib.machinery.ModuleSpec("crewai", None))
            tools_module = importlib.util.module_from_spec(importlib.machinery.ModuleSpec("crewai.tools", None))

            class DummyBaseTool:
                pass

            tools_module.BaseTool = DummyBaseTool
            sys.modules["crewai"] = crewai_module
            sys.modules["crewai.tools"] = tools_module
        repo_root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(repo_root))
        spec = importlib.util.spec_from_file_location(
            "custom_tool_module", repo_root / "src/code_genereator/tools/custom_tool.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


module = _import_module()
MyCustomTool = module.MyCustomTool
MyCustomToolInput = module.MyCustomToolInput


def test_tool_metadata_and_schema():
    """Validate tool metadata attributes and args_schema binding."""
    tool = MyCustomTool()
    assert tool.name == "Name of my tool"
    assert "Clear description" in tool.description
    assert tool.args_schema is MyCustomToolInput


def test_run_returns_expected_output():
    """Ensure _run returns the expected static output string."""
    tool = MyCustomTool()
    result = tool._run(argument="anything")
    assert result == "this is an example of a tool output, ignore it and move along."


@pytest.mark.parametrize("arg_value", ["test", "", "123", "special chars !@#"])
def test_input_schema_accepts_string_values(arg_value):
    """Validate MyCustomToolInput accepts various string values, including empty string."""
    model = MyCustomToolInput(argument=arg_value)
    assert model.argument == arg_value


def test_input_schema_missing_argument_raises():
    """Validate MyCustomToolInput raises ValidationError when argument is missing."""
    with pytest.raises(ValidationError):
        MyCustomToolInput()


@pytest.mark.parametrize("bad_value", [None, 123, 45.6, ["list"], {"dict": "value"}])
def test_input_schema_rejects_non_string_values(bad_value):
    """Validate MyCustomToolInput raises ValidationError for non-string argument types."""
    with pytest.raises(ValidationError):
        MyCustomToolInput(argument=bad_value)