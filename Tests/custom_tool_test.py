import sys
import importlib
import importlib.util
from pathlib import Path
import types
import pytest
from unittest.mock import Mock, MagicMock
from pydantic import ValidationError


@pytest.fixture(scope="session")
def custom_tool_module():
    """Provide the imported custom_tool module, with fallback handling for missing dependencies."""
    try:
        return importlib.import_module("code_genereator.tools.custom_tool")
    except Exception:
        crewai_module = types.ModuleType("crewai")
        crewai_tools_module = types.ModuleType("crewai.tools")
        crewai_tools_module.BaseTool = MagicMock
        crewai_module.tools = crewai_tools_module
        sys.modules["crewai"] = crewai_module
        sys.modules["crewai.tools"] = crewai_tools_module

        repo_root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(repo_root))
        spec = importlib.util.spec_from_file_location(
            "code_genereator.tools.custom_tool",
            repo_root / "src/code_genereator/tools/custom_tool.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def test_my_custom_tool_run_happy_path(custom_tool_module):
    """Validate that _run returns the expected static output for a normal input."""
    tool = custom_tool_module.MyCustomTool()
    output = tool._run("hello")
    assert output == "this is an example of a tool output, ignore it and move along."
    assert tool.name == "Name of my tool"
    assert "Clear description" in tool.description


@pytest.mark.parametrize("argument", ["", " ", "edge-case"])
def test_my_custom_tool_run_edge_inputs(custom_tool_module, argument):
    """Ensure _run handles edge case string inputs without errors and returns expected output."""
    tool = custom_tool_module.MyCustomTool()
    output = tool._run(argument)
    assert output == "this is an example of a tool output, ignore it and move along."


def test_my_custom_tool_input_schema_validation(custom_tool_module):
    """Verify schema validation accepts proper strings and rejects None values."""
    schema = custom_tool_module.MyCustomToolInput(argument="valid")
    assert schema.argument == "valid"
    assert custom_tool_module.MyCustomTool.args_schema is custom_tool_module.MyCustomToolInput
    with pytest.raises(ValidationError):
        custom_tool_module.MyCustomToolInput(argument=None)


def test_mock_usage_with_tool_output(custom_tool_module):
    """Use Mock objects to ensure tool output is independent of external dependencies."""
    tool = custom_tool_module.MyCustomTool()
    external_dependency = Mock()
    external_dependency.return_value = "unexpected"
    result = tool._run("input")
    assert result == "this is an example of a tool output, ignore it and move along."
    assert external_dependency.call_count == 0