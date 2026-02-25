import sys
import types
from pathlib import Path
import importlib.util
import pytest
from pydantic import ValidationError, BaseModel


def _ensure_crewai_tools_stub():
    if "crewai.tools" in sys.modules:
        return
    crewai_module = types.ModuleType("crewai")
    tools_module = types.ModuleType("crewai.tools")

    class BaseTool:
        """Minimal stub for BaseTool to allow import in tests."""
        pass

    tools_module.BaseTool = BaseTool
    crewai_module.tools = tools_module
    sys.modules["crewai"] = crewai_module
    sys.modules["crewai.tools"] = tools_module


def _import_module():
    _ensure_crewai_tools_stub()
    try:
        from src.code_genereator.tools import custom_tool
        return custom_tool
    except Exception:
        repo_root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(repo_root))
        spec = importlib.util.spec_from_file_location(
            "custom_tool", repo_root / "src/code_genereator/tools/custom_tool.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


@pytest.fixture(scope="module")
def custom_tool_module():
    """Provides the imported custom_tool module."""
    return _import_module()


def test_input_schema_valid(custom_tool_module):
    """Valid argument should populate the model correctly."""
    model = custom_tool_module.MyCustomToolInput(argument="test-value")
    assert model.argument == "test-value"
    assert isinstance(model, BaseModel)


@pytest.mark.parametrize("kwargs", [{}, {"argument": None}])
def test_input_schema_invalid(custom_tool_module, kwargs):
    """Invalid or missing argument should raise ValidationError."""
    with pytest.raises(ValidationError):
        custom_tool_module.MyCustomToolInput(**kwargs)


def test_tool_class_attributes(custom_tool_module):
    """Tool class attributes should be correctly defined."""
    tool_cls = custom_tool_module.MyCustomTool
    assert tool_cls.name == "Name of my tool"
    assert "Clear description" in tool_cls.description
    assert tool_cls.args_schema is custom_tool_module.MyCustomToolInput


@pytest.mark.parametrize("arg", ["abc", "", "123", "with spaces"])
def test_run_returns_constant_output(custom_tool_module, arg):
    """_run should return the constant output regardless of input."""
    tool = custom_tool_module.MyCustomTool()
    output = tool._run(argument=arg)
    assert output == "this is an example of a tool output, ignore it and move along."


def test_tool_instance_is_basetool_subclass(custom_tool_module):
    """MyCustomTool should be a subclass of the BaseTool stub or real BaseTool."""
    tool = custom_tool_module.MyCustomTool()
    base_class = sys.modules["crewai.tools"].BaseTool
    assert isinstance(tool, base_class)