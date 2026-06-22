# QIF_AUTOGEN_MARKER_v1
import importlib
import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel, ValidationError


EXPECTED_OUTPUT = "this is an example of a tool output, ignore it and move along."
EXPECTED_NAME = "Name of my tool"
EXPECTED_DESCRIPTION = (
    "Clear description for what this tool is useful for, your agent will need this information to use it."
)
EXPECTED_ARGUMENT_DESCRIPTION = "Description of the argument."


def _repo_root():
    current = Path(__file__).resolve()
    for parent in [current.parent, *current.parents]:
        target = parent / "src" / "code_genereator" / "tools" / "custom_tool.py"
        if target.exists():
            return parent
    return current.parents[1]


def _ensure_import_paths():
    root = _repo_root()
    src = root / "src"
    for path in (str(root), str(src)):
        if path not in sys.path:
            sys.path.insert(0, path)


def _install_crewai_stub_if_needed():
    try:
        importlib.import_module("crewai.tools")
        return
    except Exception:
        crewai_module = types.ModuleType("crewai")
        tools_module = types.ModuleType("crewai.tools")

        class BaseTool:
            pass

        tools_module.BaseTool = BaseTool
        crewai_module.tools = tools_module
        sys.modules.setdefault("crewai", crewai_module)
        sys.modules.setdefault("crewai.tools", tools_module)


def _load_module_under_test():
    _ensure_import_paths()
    _install_crewai_stub_if_needed()

    try:
        return importlib.import_module("code_genereator.tools.custom_tool")
    except Exception:
        root = _repo_root()
        module_path = root / "src" / "code_genereator" / "tools" / "custom_tool.py"
        spec = importlib.util.spec_from_file_location("custom_tool_under_test", module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["custom_tool_under_test"] = module
        spec.loader.exec_module(module)
        return module


custom_tool = _load_module_under_test()
MyCustomTool = custom_tool.MyCustomTool
MyCustomToolInput = custom_tool.MyCustomToolInput


def _field_map(model_cls):
    return getattr(model_cls, "model_fields", getattr(model_cls, "__fields__", {}))


def _field_description(field):
    return getattr(field, "description", None) or getattr(getattr(field, "field_info", None), "description", None)


def _field_required(field):
    is_required = getattr(field, "is_required", None)
    if callable(is_required):
        return is_required()
    return bool(getattr(field, "required", False))


def _class_or_pydantic_default(cls, attr):
    if hasattr(cls, attr):
        return getattr(cls, attr)
    fields = _field_map(cls)
    field = fields[attr]
    return getattr(field, "default", None)


def _model_dump(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _model_schema(model_cls):
    if hasattr(model_cls, "model_json_schema"):
        return model_cls.model_json_schema()
    return model_cls.schema()


def test_module_exports_expected_real_classes():
    """Validates that the actual module exports the expected tool and input schema classes."""
    assert custom_tool.__file__.replace("\\", "/").endswith("src/code_genereator/tools/custom_tool.py")
    assert MyCustomTool.__name__ == "MyCustomTool"
    assert MyCustomToolInput.__name__ == "MyCustomToolInput"
    assert issubclass(MyCustomToolInput, BaseModel)
    assert issubclass(MyCustomTool, custom_tool.BaseTool)


def test_input_schema_declares_required_argument_field_with_description():
    """Validates the pydantic schema field definition for the required argument input."""
    fields = _field_map(MyCustomToolInput)

    assert "argument" in fields

    field = fields["argument"]
    assert _field_required(field) is True
    assert _field_description(field) == EXPECTED_ARGUMENT_DESCRIPTION

    annotation = getattr(field, "annotation", None) or getattr(field, "outer_type_", None) or getattr(field, "type_", None)
    assert annotation is str


@pytest.mark.parametrize("value", ["hello", "", "   ", "special !@#$%^&*() text"])
def test_input_schema_accepts_string_argument_values(value):
    """Validates that valid string values are accepted and preserved by the input schema."""
    model = MyCustomToolInput(argument=value)

    assert model.argument == value
    assert _model_dump(model)["argument"] == value


def test_input_schema_rejects_missing_argument():
    """Validates that omitting the required argument field raises a pydantic validation error."""
    with pytest.raises(ValidationError):
        MyCustomToolInput()


def test_input_schema_rejects_none_argument():
    """Validates that None is not accepted for the required string argument field."""
    with pytest.raises(ValidationError):
        MyCustomToolInput(argument=None)


def test_input_schema_json_schema_contains_argument_metadata():
    """Validates that generated pydantic JSON schema includes the argument field metadata."""
    schema = _model_schema(MyCustomToolInput)

    assert "properties" in schema
    assert "argument" in schema["properties"]
    assert schema["properties"]["argument"]["description"] == EXPECTED_ARGUMENT_DESCRIPTION
    assert "required" in schema
    assert "argument" in schema["required"]


def test_tool_class_declares_expected_name_description_and_args_schema():
    """Validates the tool class metadata used by CrewAI to identify and call the tool."""
    assert _class_or_pydantic_default(MyCustomTool, "name") == EXPECTED_NAME
    assert _class_or_pydantic_default(MyCustomTool, "description") == EXPECTED_DESCRIPTION
    assert _class_or_pydantic_default(MyCustomTool, "args_schema") is MyCustomToolInput


def test_tool_run_returns_expected_output_for_normal_string_argument():
    """Validates the main happy path of the tool's _run implementation."""
    tool = MyCustomTool.__new__(MyCustomTool)

    result = tool._run("normal input")

    assert result == EXPECTED_OUTPUT
    assert isinstance(result, str)


@pytest.mark.parametrize(
    "argument",
    [
        "",
        " ",
        "ignored",
        "multi\nline\ninput",
        "unicode-åß∂ƒ©",
        None,
        0,
        123,
        {"argument": "value"},
        ["value"],
        ("value",),
    ],
)
def test_tool_run_ignores_argument_value_and_returns_constant_output(argument):
    """Validates that _run returns the documented constant output for varied argument values."""
    fake_self = MagicMock()

    result = MyCustomTool._run(fake_self, argument=argument)

    assert result == EXPECTED_OUTPUT
    assert fake_self.mock_calls == []


def test_tool_run_supports_keyword_argument_call():
    """Validates that _run can be called using the argument keyword."""
    tool = MyCustomTool.__new__(MyCustomTool)

    result = tool._run(argument="keyword input")

    assert result == EXPECTED_OUTPUT


def test_tool_run_raises_type_error_when_argument_is_missing():
    """Validates Python method-call error handling when the required argument parameter is missing."""
    fake_self = MagicMock()

    with pytest.raises(TypeError):
        MyCustomTool._run(fake_self)


def test_tool_run_raises_type_error_for_unexpected_keyword_argument():
    """Validates Python method-call error handling for unexpected keyword arguments."""
    fake_self = MagicMock()

    with pytest.raises(TypeError):
        MyCustomTool._run(fake_self, unexpected="value")


def test_tool_run_signature_matches_expected_contract():
    """Validates the public method signature annotations for _run."""
    import inspect

    signature = inspect.signature(MyCustomTool._run)

    assert list(signature.parameters) == ["self", "argument"]
    assert signature.parameters["argument"].annotation is str
    assert signature.return_annotation is str