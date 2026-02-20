import pytest
from unittest.mock import MagicMock
from typing import Type
from pydantic import BaseModel, Field, ValidationError


class BaseTool:
    """Minimal local BaseTool to emulate expected behavior."""
    name: str = ""
    description: str = ""
    args_schema: Type[BaseModel] = BaseModel

    def run(self, **kwargs):
        if self.args_schema:
            model = self.args_schema(**kwargs)
            data = model.dict()
        else:
            data = kwargs
        return self._run(**data)

    def _run(self, **kwargs):
        raise NotImplementedError


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")


class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        return "this is an example of a tool output, ignore it and move along."


@pytest.fixture
def tool_instance():
    """Provide a fresh tool instance for tests."""
    return MyCustomTool()


def test_tool_run_happy_path_returns_expected_output(tool_instance):
    """Validate that running the tool with valid input returns the expected output."""
    result = tool_instance.run(argument="hello")
    assert result == "this is an example of a tool output, ignore it and move along."


@pytest.mark.parametrize("arg", ["", "   ", "edge-case"])
def test_tool_run_allows_empty_or_whitespace_argument(tool_instance, arg):
    """Ensure the tool accepts empty or whitespace arguments as valid strings."""
    result = tool_instance.run(argument=arg)
    assert result == "this is an example of a tool output, ignore it and move along."


def test_tool_run_raises_validation_error_on_none_argument(tool_instance):
    """Confirm that passing None as argument raises a validation error."""
    with pytest.raises(ValidationError):
        tool_instance.run(argument=None)


def test_tool_metadata_and_schema_definition():
    """Verify tool metadata attributes and schema class are correctly defined."""
    tool = MyCustomTool()
    assert tool.name == "Name of my tool"
    assert "Clear description" in tool.description
    assert tool.args_schema is MyCustomToolInput


def test_tool_run_calls_internal_run_with_validated_data(tool_instance):
    """Ensure BaseTool.run validates input and calls _run with processed data."""
    tool_instance._run = MagicMock(return_value="mocked-output")
    result = tool_instance.run(argument="validated")
    tool_instance._run.assert_called_once_with(argument="validated")
    assert result == "mocked-output"