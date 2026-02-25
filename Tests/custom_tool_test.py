import sys
from pathlib import Path
import importlib
import importlib.util
import types
from unittest.mock import MagicMock
import pytest
from pydantic import ValidationError

# TEST PLAN
# - test_tool_class_attributes
# - test_tool_run_returns_expected_output
# - test_tool_run_handles_edge_string_inputs
# - test_tool_run_accepts_none_argument
# - test_input_schema_validates_required_field
# - test_input_schema_accepts_string
# - test_input_schema_coerces_or_rejects_non_string
# - test_input_schema_description_present
# - test_mocking_external_dependency_does_not_affect_run

def _ensure_crewai_tools_available():
    if "crewai.tools" in sys.modules:
        return
    crewai_module = types.ModuleType("crewai")
    tools_module = types.ModuleType("crewai.tools")
    class BaseTool:
        pass
    tools_module.BaseTool = BaseTool
    crewai_module.tools = tools_module
    sys.modules["crewai"] = crewai_module
    sys.modules["crewai.tools"] = tools_module

def _import_custom_tool_module():
    try:
        _ensure_crewai_tools_available()
        return importlib.import_module("code_genereator.tools.custom_tool")
    except Exception:
        _ensure_crewai_tools_available()
        repo_root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(repo_root))
        spec = importlib.util.spec_from_file_location(
            "module_under_test",
            repo_root / "src/code_genereator/tools/custom_tool.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

module = _import_custom_tool_module()
MyCustomTool = module.MyCustomTool
MyCustomToolInput = module.MyCustomToolInput
BaseTool = sys.modules["crewai.tools"].BaseTool

def test_tool_class_attributes():
    """Validate class-level metadata attributes and schema linkage."""
    assert MyCustomTool.name == "Name of my tool"
    assert "Clear description" in MyCustomTool.description
    assert MyCustomTool.args_schema is MyCustomToolInput
    assert issubclass(MyCustomTool, BaseTool)

def test_tool_run_returns_expected_output():
    """Ensure _run returns the expected constant output for typical input."""
    tool = MyCustomTool()
    output = tool._run("hello")
    assert output == "this is an example of a tool output, ignore it and move along."

@pytest.mark.parametrize("argument", ["", "   ", "special!@#"])
def test_tool_run_handles_edge_string_inputs(argument):
    """Ensure _run returns expected output for edge string inputs including empty and whitespace."""
    tool = MyCustomTool()
    output = tool._run(argument)
    assert output == "this is an example of a tool output, ignore it and move along."

def test_tool_run_accepts_none_argument():
    """Ensure _run ignores argument type and still returns expected output when None is provided."""
    tool = MyCustomTool()
    output = tool._run(None)
    assert output == "this is an example of a tool output, ignore it and move along."

def test_input_schema_validates_required_field():
    """Validate that the input schema requires the argument field."""
    with pytest.raises(ValidationError):
        MyCustomToolInput()

def test_input_schema_accepts_string():
    """Validate that the input schema accepts a valid string argument."""
    instance = MyCustomToolInput(argument="valid")
    assert instance.argument == "valid"

def test_input_schema_coerces_or_rejects_non_string():
    """Validate behavior for non-string input: either coercion or validation error."""
    try:
        instance = MyCustomToolInput(argument=123)
    except ValidationError:
        assert True
    else:
        assert isinstance(instance.argument, str)
        assert instance.argument == "123"

def test_input_schema_description_present():
    """Verify that the schema includes the argument description."""
    instance = MyCustomToolInput(argument="value")
    if hasattr(instance, "schema"):
        schema = instance.schema()
    else:
        schema = instance.model_json_schema()
    assert "argument" in schema["properties"]
    assert schema["properties"]["argument"]["description"] == "Description of the argument."

def test_mocking_external_dependency_does_not_affect_run():
    """Ensure that mocking external objects does not alter _run behavior."""
    tool = MyCustomTool()
    dummy = MagicMock()
    dummy.side_effect = Exception("should not be called")
    output = tool._run("input")
    assert output == "this is an example of a tool output, ignore it and move along."