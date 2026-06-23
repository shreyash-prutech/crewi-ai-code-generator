import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from pydantic import ValidationError

# Try direct import first
try:
    from src.code_genereator.tools.custom_tool import MyCustomTool, MyCustomToolInput
except ImportError:
    # Fallback to dynamic import
    import importlib.util
    
    REPO_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(REPO_ROOT))
    
    spec = importlib.util.spec_from_file_location(
        "custom_tool", 
        REPO_ROOT / "src/code_genereator/tools/custom_tool.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    MyCustomTool = module.MyCustomTool
    MyCustomToolInput = module.MyCustomToolInput


class TestMyCustomToolInput:
    """Test cases for MyCustomToolInput schema validation."""
    
    def test_valid_input_creation(self):
        """Test that valid input creates MyCustomToolInput instance successfully."""
        input_data = MyCustomToolInput(argument="test argument")
        assert input_data.argument == "test argument"
        assert isinstance(input_data.argument, str)
    
    def test_empty_string_argument(self):
        """Test that empty string is accepted as valid input."""
        input_data = MyCustomToolInput(argument="")
        assert input_data.argument == ""
    
    def test_missing_argument_raises_validation_error(self):
        """Test that missing required argument raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MyCustomToolInput()
        assert "argument" in str(exc_info.value)
    
    def test_none_argument_raises_validation_error(self):
        """Test that None argument raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MyCustomToolInput(argument=None)
        assert "argument" in str(exc_info.value)
    
    @pytest.mark.parametrize("test_input", [
        "simple text",
        "text with spaces",
        "text-with-dashes",
        "text_with_underscores",
        "123456",
        "special!@#$%characters"
    ])
    def test_various_string_inputs(self, test_input):
        """Test that various string formats are accepted."""
        input_data = MyCustomToolInput(argument=test_input)
        assert input_data.argument == test_input


class TestMyCustomTool:
    """Test cases for MyCustomTool functionality."""
    
    @pytest.fixture
    def custom_tool(self):
        """Fixture to create MyCustomTool instance."""
        return MyCustomTool()
    
    def test_tool_initialization(self, custom_tool):
        """Test that MyCustomTool initializes with correct attributes."""
        assert custom_tool.name == "Name of my tool"
        assert "Clear description for what this tool is useful for" in custom_tool.description
        assert custom_tool.args_schema == MyCustomToolInput
    
    def test_tool_inherits_from_base_tool(self, custom_tool):
        """Test that MyCustomTool properly inherits from BaseTool."""
        # Check if it has the expected BaseTool methods/attributes
        assert hasattr(custom_tool, '_run')
        assert hasattr(custom_tool, 'name')
        assert hasattr(custom_tool, 'description')
        assert hasattr(custom_tool, 'args_schema')
    
    def test_run_method_with_valid_argument(self, custom_tool):
        """Test that _run method returns expected output with valid argument."""
        result = custom_tool._run("test argument")
        assert isinstance(result, str)
        assert result == "this is an example of a tool output, ignore it and move along."
    
    def test_run_method_with_empty_string(self, custom_tool):
        """Test that _run method handles empty string argument."""
        result = custom_tool._run("")
        assert isinstance(result, str)
        assert result == "this is an example of a tool output, ignore it and move along."
    
    def test_run_method_with_long_argument(self, custom_tool):
        """Test that _run method handles long string arguments."""
        long_argument = "a" * 1000
        result = custom_tool._run(long_argument)
        assert isinstance(result, str)
        assert result == "this is an example of a tool output, ignore it and move along."
    
    @pytest.mark.parametrize("test_argument", [
        "simple text",
        "text with special chars !@#$%",
        "multiline\ntext\nwith\nnewlines",
        "unicode text: 你好世界",
        "123456789",
        "mixed123text!@#"
    ])
    def test_run_method_with_various_arguments(self, custom_tool, test_argument):
        """Test that _run method consistently returns same output regardless of input."""
        result = custom_tool._run(test_argument)
        assert isinstance(result, str)
        assert result == "this is an example of a tool output, ignore it and move along."
    
    def test_tool_name_is_string(self, custom_tool):
        """Test that tool name is a string."""
        assert isinstance(custom_tool.name, str)
        assert len(custom_tool.name) > 0
    
    def test_tool_description_is_string(self, custom_tool):
        """Test that tool description is a string."""
        assert isinstance(custom_tool.description, str)
        assert len(custom_tool.description) > 0
    
    def test_args_schema_is_correct_type(self, custom_tool):
        """Test that args_schema is set to the correct BaseModel subclass."""
        assert custom_tool.args_schema == MyCustomToolInput
        assert issubclass(custom_tool.args_schema, BaseModel)
    
    def test_tool_can_validate_input_schema(self, custom_tool):
        """Test that tool can validate input using its schema."""
        # Valid input should not raise an error
        valid_input = custom_tool.args_schema(argument="test")
        assert valid_input.argument == "test"
        
        # Invalid input should raise ValidationError
        with pytest.raises(ValidationError):
            custom_tool.args_schema()


class TestMyCustomToolIntegration:
    """Integration tests for MyCustomTool with its input schema."""
    
    def test_tool_with_schema_validation_success(self):
        """Test complete workflow with valid input schema."""
        tool = MyCustomTool()
        input_schema = MyCustomToolInput(argument="integration test")
        
        result = tool._run(input_schema.argument)
        
        assert isinstance(result, str)
        assert result == "this is an example of a tool output, ignore it and move along."
    
    def test_tool_schema_field_description(self):
        """Test that input schema has proper field description."""
        tool = MyCustomTool()
        schema_fields = tool.args_schema.__fields__
        
        assert 'argument' in schema_fields
        assert schema_fields['argument'].field_info.description == "Description of the argument."
    
    def test_tool_schema_field_is_required(self):
        """Test that argument field is required in schema."""
        tool = MyCustomTool()
        schema_fields = tool.args_schema.__fields__
        
        assert 'argument' in schema_fields
        assert schema_fields['argument'].is_required()