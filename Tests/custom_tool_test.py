import sys
import importlib
import types
from pathlib import Path
import pytest
from pydantic import BaseModel, ValidationError


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_module():
    sys.path.insert(0, str(REPO_ROOT / "src"))
    try:
        return importlib.import_module("code_genereator.tools.custom_tool")
    except Exception:
        crewai = types.ModuleType("crewai")
        tools = types.ModuleType("crewai.tools")

        class BaseTool:
            pass

        tools.BaseTool = BaseTool
        crewai.tools = tools
        sys.modules.setdefault("crewai", crewai)
        sys.modules.setdefault("crewai.tools", tools)
        try:
            return importlib.import_module("code_genereator.tools.custom_tool")
        except Exception:
            spec = importlib.util.spec_from_file_location(
                "module_under_test", REPO_ROOT / "src" / "code_genereator" / "tools" / "custom_tool.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module


@pytest.fixture(scope="session")
def custom_tool_module():
    """Provides the imported custom_tool module for tests."""
    return _load_module()


def _get_field_description(model_cls, field_name):
    if hasattr(model_cls, "model_fields"):
        return model_cls.model_fields[field_name].description
    return model_cls.__fields__[field_name].field_info.description


def test_input_schema_validates_argument(custom_tool_module):
    """Valid input should create a MyCustomToolInput instance with the correct argument."""
    MyCustomToolInput = custom_tool_module.MyCustomToolInput
    instance = MyCustomToolInput(argument="valid")
    assert instance.argument == "valid"


def test_input_schema_allows_empty_string(custom_tool_module):
    """Empty string should be accepted as a valid argument value."""
    MyCustomToolInput = custom_tool_module.MyCustomToolInput
    instance = MyCustomToolInput(argument="")
    assert instance.argument == ""


def test_input_schema_missing_argument_raises(custom_tool_module):
    """Missing required argument should raise a ValidationError."""
    MyCustomToolInput = custom_tool_module.MyCustomToolInput
    with pytest.raises(ValidationError):
        MyCustomToolInput()


def test_input_schema_none_argument_raises(custom_tool_module):
    """None as argument should raise a ValidationError for required field."""
    MyCustomToolInput = custom_tool_module.MyCustomToolInput
    with pytest.raises(ValidationError):
        MyCustomToolInput(argument=None)


def test_input_schema_field_description(custom_tool_module):
    """The field description should match the expected description text."""
    MyCustomToolInput = custom_tool_module.MyCustomToolInput
    desc = _get_field_description(MyCustomToolInput, "argument")
    assert desc == "Description of the argument."


def test_custom_tool_class_attributes(custom_tool_module):
    """MyCustomTool class should define expected metadata attributes."""
    MyCustomTool = custom_tool_module.MyCustomTool
    assert MyCustomTool.name == "Name of my tool"
    assert "Clear description for what this tool is useful for" in MyCustomTool.description
    assert MyCustomTool.args_schema is custom_tool_module.MyCustomToolInput
    assert issubclass(MyCustomTool.args_schema, BaseModel)


def test_custom_tool_run_returns_expected_output(custom_tool_module):
    """_run should return the hardcoded output string regardless of input."""
    MyCustomTool = custom_tool_module.MyCustomTool
    tool_instance = object.__new__(MyCustomTool)
    result = MyCustomTool._run(tool_instance, argument="anything")
    assert result == "this is an example of a tool output, ignore it and move along."


def test_custom_tool_run_with_empty_argument(custom_tool_module):
    """_run should still return output even when given an empty argument."""
    MyCustomTool = custom_tool_module.MyCustomTool
    tool_instance = object.__new__(MyCustomTool)
    result = MyCustomTool._run(tool_instance, argument="")
    assert result == "this is an example of a tool output, ignore it and move along."


def test_custom_tool_run_with_none_argument(custom_tool_module):
    """_run should not enforce argument type and returns output with None input."""
    MyCustomTool = custom_tool_module.MyCustomTool
    tool_instance = object.__new__(MyCustomTool)
    result = MyCustomTool._run(tool_instance, argument=None)
    assert result == "this is an example of a tool output, ignore it and move along."