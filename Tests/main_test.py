import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
from datetime import datetime
import importlib.util

# Import the module under test
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

try:
    from src.code_genereator.main import save_execution_log, SoftwareDevFlow
    from src.code_genereator.state import DevelopmentState
except ImportError:
    # Fallback to dynamic import
    spec = importlib.util.spec_from_file_location("main_module", REPO_ROOT / "src/code_genereator/main.py")
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    save_execution_log = main_module.save_execution_log
    SoftwareDevFlow = main_module.SoftwareDevFlow
    
    # Import state module
    state_spec = importlib.util.spec_from_file_location("state_module", REPO_ROOT / "src/code_genereator/state.py")
    state_module = importlib.util.module_from_spec(state_spec)
    state_spec.loader.exec_module(state_module)
    DevelopmentState = state_module.DevelopmentState


@pytest.fixture
def mock_development_state():
    """Create a mock DevelopmentState for testing."""
    state = Mock(spec=DevelopmentState)
    state.id = "test-flow-123"
    state.status = "completed"
    state.requirement = "Build a simple todo app"
    state.plan = "Technical specification for todo app with React frontend and FastAPI backend"
    state.database_code = "CREATE TABLE todos (id SERIAL PRIMARY KEY, title VARCHAR(255), completed BOOLEAN);"
    state.backend_code = "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/todos')\ndef get_todos(): return []"
    state.frontend_code = "import React from 'react';\nconst TodoApp = () => <div>Todo App</div>;\nexport default TodoApp;"
    state.final_report = "All components implemented successfully. Code quality is good."
    return state


@pytest.fixture
def empty_development_state():
    """Create a DevelopmentState with empty/None values."""
    state = Mock(spec=DevelopmentState)
    state.id = "empty-flow-456"
    state.status = "failed"
    state.requirement = "Empty requirement test"
    state.plan = ""
    state.database_code = ""
    state.backend_code = ""
    state.frontend_code = ""
    state.final_report = ""
    return state


@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
@patch('os.path.dirname')
@patch('os.path.join')
@patch('datetime')
def test_save_execution_log_happy_path(mock_datetime, mock_join, mock_dirname, mock_file, mock_makedirs, mock_development_state):
    """Test save_execution_log with complete state data."""
    # Setup mocks
    mock_datetime.now.return_value.strftime.side_effect = lambda fmt: {
        "%Y%m%d_%H%M%S": "20231215_143022",
        "%Y-%m-%d %H:%M:%S": "2023-12-15 14:30:22"
    }[fmt]
    
    mock_dirname.return_value = "/project/root"
    mock_join.side_effect = lambda *args: "/".join(args)
    
    # Call the function
    result = save_execution_log(mock_development_state, "test/logs")
    
    # Verify directory creation
    mock_makedirs.assert_called_once_with("/project/root/test/logs", exist_ok=True)
    
    # Verify file operations
    expected_filename = "/project/root/test/logs/execution_log_20231215_143022.md"
    mock_file.assert_called_once_with(expected_filename, 'w', encoding='utf-8')
    
    # Verify content was written
    written_content = mock_file().write.call_args[0][0]
    assert "# Agentic Software Factory - Execution Log" in written_content
    assert "test-flow-123" in written_content
    assert "completed" in written_content
    assert "Build a simple todo app" in written_content
    assert "Technical specification for todo app" in written_content
    assert "CREATE TABLE todos" in written_content
    assert "from fastapi import FastAPI" in written_content
    assert "import React from 'react'" in written_content
    assert "All components implemented successfully" in written_content
    
    # Verify return value
    assert result == expected_filename


@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
@patch('os.path.dirname')
@patch('os.path.join')
@patch('datetime')
def test_save_execution_log_empty_state(mock_datetime, mock_join, mock_dirname, mock_file, mock_makedirs, empty_development_state):
    """Test save_execution_log with empty/None state values."""
    # Setup mocks
    mock_datetime.now.return_value.strftime.side_effect = lambda fmt: {
        "%Y%m%d_%H%M%S": "20231215_150000",
        "%Y-%m-%d %H:%M:%S": "2023-12-15 15:00:00"
    }[fmt]
    
    mock_dirname.return_value = "/project"
    mock_join.side_effect = lambda *args: "/".join(args)
    
    # Call the function
    result = save_execution_log(empty_development_state)
    
    # Verify default log directory is used
    mock_makedirs.assert_called_once_with("/project/dist/logs", exist_ok=True)
    
    # Verify content handles empty values
    written_content = mock_file().write.call_args[0][0]
    assert "empty-flow-456" in written_content
    assert "failed" in written_content
    assert "Empty requirement test" in written_content
    assert "❌" in written_content  # Should show failed status for empty fields
    assert "0 chars" in written_content  # Should show 0 character count for empty strings


@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
@patch('os.path.dirname')
@patch('os.path.join')
def test_save_execution_log_file_operations(mock_join, mock_dirname, mock_file, mock_makedirs, mock_development_state):
    """Test save_execution_log file system operations and error handling."""
    mock_dirname.return_value = "/base"
    mock_join.side_effect = lambda *args: "/".join(args)
    
    # Test successful execution
    result = save_execution_log(mock_development_state, "custom/path")
    
    # Verify path construction
    assert mock_dirname.call_count >= 3  # Called multiple times for path resolution
    mock_makedirs.assert_called_once()
    mock_file.assert_called_once()
    
    # Verify the file was opened with correct parameters
    call_args = mock_file.call_args
    assert call_args[1]['encoding'] == 'utf-8'
    assert 'w' in call_args[0]


def test_software_dev_flow_initialization():
    """Test SoftwareDevFlow class initialization."""
    flow = SoftwareDevFlow()
    
    # Verify it's a Flow instance
    assert hasattr(flow, 'kickoff')
    assert hasattr(flow, 'plot')
    
    # Verify it has the expected methods
    assert hasattr(flow, 'initialize_development')
    assert hasattr(flow, 'planning_phase')
    assert hasattr(flow, 'engineering_phase')
    assert hasattr(flow, 'judging_phase')


@patch('code_genereator.main.save_execution_log')
def test_software_dev_flow_kickoff_integration(mock_save_log):
    """Test SoftwareDevFlow kickoff method integration."""
    flow = SoftwareDevFlow()
    
    # Mock the save_execution_log to avoid file operations
    mock_save_log.return_value = "/path/to/log.md"
    
    # Test that flow can be instantiated and has required methods
    assert callable(getattr(flow, 'kickoff', None))
    
    # Verify the flow has the expected state type annotation
    assert hasattr(flow, '__orig_bases__')


@patch('os.makedirs', side_effect=OSError("Permission denied"))
@patch('os.path.dirname')
@patch('os.path.join')
def test_save_execution_log_directory_creation_error(mock_join, mock_dirname, mock_makedirs, mock_development_state):
    """Test save_execution_log when directory creation fails."""
    mock_dirname.return_value = "/readonly"
    mock_join.side_effect = lambda *args: "/".join(args)
    
    # Should raise the OSError from makedirs
    with pytest.raises(OSError, match="Permission denied"):
        save_execution_log(mock_development_state)


@patch('os.makedirs')
@patch('builtins.open', side_effect=IOError("Disk full"))
@patch('os.path.dirname')
@patch('os.path.join')
@patch('datetime')
def test_save_execution_log_file_write_error(mock_datetime, mock_join, mock_dirname, mock_file, mock_makedirs, mock_development_state):
    """Test save_execution_log when file writing fails."""
    mock_datetime.now.return_value.strftime.return_value = "20231215_160000"
    mock_dirname.return_value = "/project"
    mock_join.side_effect = lambda *args: "/".join(args)
    
    # Should raise the IOError from file operations
    with pytest.raises(IOError, match="Disk full"):
        save_execution_log(mock_development_state)


def test_save_execution_log_content_formatting(mock_development_state):
    """Test the markdown content formatting in save_execution_log."""
    with patch('os.makedirs'), \
         patch('builtins.open', mock_open()) as mock_file, \
         patch('os.path.dirname', return_value="/base"), \
         patch('os.path.join', side_effect=lambda *args: "/".join(args)), \
         patch('datetime') as mock_datetime:
        
        mock_datetime.now.return_value.strftime.side_effect = lambda fmt: {
            "%Y%m%d_%H%M%S": "20231215_170000",
            "%Y-%m-%d %H:%M:%S": "2023-12-15 17:00:00"
        }[fmt]
        
        save_execution_log(mock_development_state)
        
        written_content = mock_file().write.call_args[0][0]
        
        # Test markdown structure
        assert written_content.startswith("# Agentic Software Factory - Execution Log")
        assert "## Original Requirement" in written_content
        assert "## PHASE 1: Planning Crew Output" in written_content
        assert "## PHASE 2: Engineering Crew Output" in written_content
        assert "## PHASE 3: Judge Crew Output" in written_content
        assert "## Summary" in written_content
        
        # Test code blocks
        assert "```sql" in written_content
        assert "```python" in written_content
        assert "```tsx" in written_content
        
        # Test table formatting
        assert "| Artifact | Status | Size |" in written_content
        assert "|----------|--------|------|" in written_content


@pytest.mark.parametrize("requirement,expected_in_content", [
    ("Simple todo app", "Simple todo app"),
    ("E-commerce platform with payment integration", "E-commerce platform with payment integration"),
    ("", ""),
    ("Multi-line\nrequirement\nwith breaks", "Multi-line\nrequirement\nwith breaks")
])
def test_save_execution_log_various_requirements(requirement, expected_in_content):
    """Test save_execution_log with various requirement formats."""
    state = Mock(spec=DevelopmentState)
    state.id = "param-test"
    state.status = "completed"
    state.requirement = requirement
    state.plan = "Test plan"
    state.database_code = "SELECT 1;"
    state.backend_code = "print('hello')"
    state.frontend_code = "console.log('test');"
    state.final_report = "Test report"
    
    with patch('os.makedirs'), \
         patch('builtins.open', mock_open()) as mock_file, \
         patch('os.path.dirname', return_value="/test"), \
         patch('os.path.join', side_effect=lambda *args: "/".join(args)), \
         patch('datetime') as mock_datetime:
        
        mock_datetime.now.return_value.strftime.return_value = "test_timestamp"
        
        save_execution_log(state)
        
        written_content = mock_file().write.call_args[0][0]
        assert expected_in_content in written_content