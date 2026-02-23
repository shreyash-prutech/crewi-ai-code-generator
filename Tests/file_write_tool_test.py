import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import sys
import importlib.util

# Import the module under test
try:
    from src.code_genereator.tools.file_write_tool import FileWriteTool, FileWriteToolInput
except ImportError:
    # Fallback to dynamic import
    REPO_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(REPO_ROOT))
    
    spec = importlib.util.spec_from_file_location(
        "file_write_tool", 
        REPO_ROOT / "src/code_genereator/tools/file_write_tool.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    FileWriteTool = module.FileWriteTool
    FileWriteToolInput = module.FileWriteToolInput


@pytest.fixture
def file_write_tool():
    """Create a FileWriteTool instance for testing."""
    return FileWriteTool()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing file operations."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_file_write_tool_input_schema():
    """Test that FileWriteToolInput schema validates correctly."""
    # Test valid input
    valid_input = FileWriteToolInput(
        file_path="dist/backend/main.py",
        content="print('Hello World')"
    )
    assert valid_input.file_path == "dist/backend/main.py"
    assert valid_input.content == "print('Hello World')"
    
    # Test with empty content
    empty_content_input = FileWriteToolInput(
        file_path="dist/test.py",
        content=""
    )
    assert empty_content_input.content == ""
    
    # Test missing required fields should raise validation error
    with pytest.raises(Exception):
        FileWriteToolInput()


def test_file_write_tool_properties(file_write_tool):
    """Test that FileWriteTool has correct properties."""
    assert file_write_tool.name == "file_write_tool"
    assert "Writes content to a file" in file_write_tool.description
    assert file_write_tool.args_schema == FileWriteToolInput


@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
@patch('os.path.dirname')
@patch('os.path.join')
def test_file_write_tool_run_success(mock_join, mock_dirname, mock_file, mock_makedirs, file_write_tool):
    """Test successful file writing operation."""
    # Setup mocks
    mock_dirname.side_effect = [
        "/project/src/code_genereator/tools",  # First call for __file__
        "/project/src/code_genereator",        # Second call
        "/project/src",                        # Third call
        "/project",                           # Fourth call (base_dir)
        "/project/dist/backend"               # Fifth call for parent_dir
    ]
    mock_join.return_value = "/project/dist/backend/main.py"
    
    # Execute
    result = file_write_tool._run("dist/backend/main.py", "print('Hello World')")
    
    # Verify
    assert result == "Successfully wrote file to: dist/backend/main.py"
    mock_makedirs.assert_called_once_with("/project/dist/backend", exist_ok=True)
    mock_file.assert_called_once_with("/project/dist/backend/main.py", 'w', encoding='utf-8')
    mock_file().write.assert_called_once_with("print('Hello World')")


@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
@patch('os.path.dirname')
@patch('os.path.join')
def test_file_write_tool_run_with_empty_content(mock_join, mock_dirname, mock_file, mock_makedirs, file_write_tool):
    """Test file writing with empty content."""
    # Setup mocks
    mock_dirname.side_effect = [
        "/project/src/code_genereator/tools",
        "/project/src/code_genereator",
        "/project/src",
        "/project",
        "/project/dist"
    ]
    mock_join.return_value = "/project/dist/empty.txt"
    
    # Execute
    result = file_write_tool._run("dist/empty.txt", "")
    
    # Verify
    assert result == "Successfully wrote file to: dist/empty.txt"
    mock_file().write.assert_called_once_with("")


@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
@patch('os.path.dirname')
@patch('os.path.join')
def test_file_write_tool_run_no_parent_directory(mock_join, mock_dirname, mock_file, mock_makedirs, file_write_tool):
    """Test file writing when parent directory is empty."""
    # Setup mocks
    mock_dirname.side_effect = [
        "/project/src/code_genereator/tools",
        "/project/src/code_genereator",
        "/project/src",
        "/project",
        ""  # Empty parent directory
    ]
    mock_join.return_value = "/project/test.py"
    
    # Execute
    result = file_write_tool._run("test.py", "content")
    
    # Verify
    assert result == "Successfully wrote file to: test.py"
    mock_makedirs.assert_not_called()  # Should not create directories for empty parent
    mock_file().write.assert_called_once_with("content")


@patch('os.makedirs')
@patch('builtins.open', side_effect=PermissionError("Permission denied"))
@patch('os.path.dirname')
@patch('os.path.join')
def test_file_write_tool_run_permission_error(mock_join, mock_dirname, mock_file, mock_makedirs, file_write_tool):
    """Test handling of permission errors during file writing."""
    # Setup mocks
    mock_dirname.side_effect = [
        "/project/src/code_genereator/tools",
        "/project/src/code_genereator",
        "/project/src",
        "/project",
        "/project/dist"
    ]
    mock_join.return_value = "/project/dist/protected.py"
    
    # Execute
    result = file_write_tool._run("dist/protected.py", "content")
    
    # Verify
    assert result == "Error: Permission denied when writing to dist/protected.py"


@patch('os.makedirs', side_effect=OSError("Disk full"))
@patch('os.path.dirname')
@patch('os.path.join')
def test_file_write_tool_run_makedirs_error(mock_join, mock_dirname, mock_makedirs, file_write_tool):
    """Test handling of errors during directory creation."""
    # Setup mocks
    mock_dirname.side_effect = [
        "/project/src/code_genereator/tools",
        "/project/src/code_genereator",
        "/project/src",
        "/project",
        "/project/dist/deep/nested"
    ]
    mock_join.return_value = "/project/dist/deep/nested/file.py"
    
    # Execute
    result = file_write_tool._run("dist/deep/nested/file.py", "content")
    
    # Verify
    assert result == "Error writing file dist/deep/nested/file.py: Disk full"


@patch('os.makedirs')
@patch('builtins.open', side_effect=UnicodeEncodeError('utf-8', 'test', 0, 1, 'invalid'))
@patch('os.path.dirname')
@patch('os.path.join')
def test_file_write_tool_run_unicode_error(mock_join, mock_dirname, mock_file, mock_makedirs, file_write_tool):
    """Test handling of unicode encoding errors."""
    # Setup mocks
    mock_dirname.side_effect = [
        "/project/src/code_genereator/tools",
        "/project/src/code_genereator",
        "/project/src",
        "/project",
        "/project/dist"
    ]
    mock_join.return_value = "/project/dist/unicode_test.py"
    
    # Execute
    result = file_write_tool._run("dist/unicode_test.py", "invalid unicode content")
    
    # Verify
    assert "Error writing file dist/unicode_test.py:" in result
    assert "invalid" in result


@pytest.mark.parametrize("file_path,content,expected_success", [
    ("dist/backend/main.py", "print('Hello')", True),
    ("dist/frontend/index.html", "<html></html>", True),
    ("dist/config.json", '{"key": "value"}', True),
    ("dist/deep/nested/path/file.txt", "nested content", True),
    ("simple.txt", "simple content", True),
])
@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
@patch('os.path.dirname')
@patch('os.path.join')
def test_file_write_tool_run_parametrized(mock_join, mock_dirname, mock_file, mock_makedirs, 
                                         file_path, content, expected_success, file_write_tool):
    """Test file writing with various file paths and content."""
    # Setup mocks
    mock_dirname.side_effect = [
        "/project/src/code_genereator/tools",
        "/project/src/code_genereator",
        "/project/src",
        "/project",
        f"/project/{os.path.dirname(file_path)}" if os.path.dirname(file_path) else ""
    ]
    mock_join.return_value = f"/project/{file_path}"
    
    # Execute
    result = file_write_tool._run(file_path, content)
    
    # Verify
    if expected_success:
        assert result == f"Successfully wrote file to: {file_path}"
        mock_file().write.assert_called_once_with(content)
    else:
        assert "Error" in result


def test_file_write_tool_integration_with_real_filesystem(temp_dir):
    """Integration test using real filesystem operations."""
    tool = FileWriteTool()
    
    # Create a test file path within temp directory
    test_file_path = os.path.join(temp_dir, "test_output.py")
    test_content = "# This is a test file\nprint('Integration test')"
    
    # Mock the base directory calculation to use our temp directory
    with patch('os.path.dirname') as mock_dirname:
        mock_dirname.side_effect = [
            "/fake/src/code_genereator/tools",
            "/fake/src/code_genereator",
            "/fake/src",
            temp_dir,  # Return temp_dir as base_dir
            os.path.dirname(test_file_path)  # Parent directory
        ]
        
        with patch('os.path.join', side_effect=os.path.join):
            result = tool._run("test_output.py", test_content)
    
    # Verify the result
    assert "Successfully wrote file to: test_output.py" in result
    
    # Verify the file was actually created and has correct content
    assert os.path.exists(test_file_path)
    with open(test_file_path, 'r', encoding='utf-8') as f:
        actual_content = f.read()
    assert actual_content == test_content