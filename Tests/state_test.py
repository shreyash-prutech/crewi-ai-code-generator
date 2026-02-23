import pytest
import uuid
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
import sys
from pathlib import Path

# Import the actual module
try:
    from src.code_genereator.state import DevelopmentState
except ImportError:
    # Fallback to dynamic import
    import importlib.util
    REPO_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location("state", REPO_ROOT / "src/code_genereator/state.py")
    state_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(state_module)
    DevelopmentState = state_module.DevelopmentState


def test_development_state_default_initialization():
    """Test that DevelopmentState can be created with default values."""
    state = DevelopmentState()
    
    assert isinstance(state.id, str)
    assert len(state.id) > 0
    assert state.requirement == ""
    assert state.plan == ""
    assert state.database_code == ""
    assert state.backend_code == ""
    assert state.frontend_code == ""
    assert state.final_report == ""
    assert state.project_name is None
    assert state.status == "initialized"


def test_development_state_with_custom_values():
    """Test that DevelopmentState can be created with custom values."""
    custom_id = "test-id-123"
    requirement = "Build a web application"
    plan = "Technical specification for web app"
    database_code = "CREATE TABLE users (id INT PRIMARY KEY);"
    backend_code = "from flask import Flask\napp = Flask(__name__)"
    frontend_code = "<html><body>Hello World</body></html>"
    final_report = "All tests passed successfully"
    project_name = "MyWebApp"
    status = "completed"
    
    state = DevelopmentState(
        id=custom_id,
        requirement=requirement,
        plan=plan,
        database_code=database_code,
        backend_code=backend_code,
        frontend_code=frontend_code,
        final_report=final_report,
        project_name=project_name,
        status=status
    )
    
    assert state.id == custom_id
    assert state.requirement == requirement
    assert state.plan == plan
    assert state.database_code == database_code
    assert state.backend_code == backend_code
    assert state.frontend_code == frontend_code
    assert state.final_report == final_report
    assert state.project_name == project_name
    assert state.status == status


def test_development_state_id_generation():
    """Test that each DevelopmentState instance gets a unique ID by default."""
    state1 = DevelopmentState()
    state2 = DevelopmentState()
    
    assert state1.id != state2.id
    assert isinstance(state1.id, str)
    assert isinstance(state2.id, str)
    assert len(state1.id) > 0
    assert len(state2.id) > 0


@patch('uuid.uuid4')
def test_development_state_id_uses_uuid4(mock_uuid4):
    """Test that the ID field uses uuid.uuid4() for generation."""
    mock_uuid_obj = MagicMock()
    mock_uuid_obj.__str__ = MagicMock(return_value="mocked-uuid-string")
    mock_uuid4.return_value = mock_uuid_obj
    
    state = DevelopmentState()
    
    mock_uuid4.assert_called_once()
    assert state.id == "mocked-uuid-string"


def test_development_state_partial_initialization():
    """Test that DevelopmentState can be created with only some fields set."""
    state = DevelopmentState(
        requirement="Create a REST API",
        status="planning"
    )
    
    assert isinstance(state.id, str)
    assert state.requirement == "Create a REST API"
    assert state.plan == ""
    assert state.database_code == ""
    assert state.backend_code == ""
    assert state.frontend_code == ""
    assert state.final_report == ""
    assert state.project_name is None
    assert state.status == "planning"


def test_development_state_field_types():
    """Test that all fields accept the correct types."""
    state = DevelopmentState(
        id="string-id",
        requirement="string requirement",
        plan="string plan",
        database_code="string database code",
        backend_code="string backend code",
        frontend_code="string frontend code",
        final_report="string final report",
        project_name="string project name",
        status="string status"
    )
    
    assert isinstance(state.id, str)
    assert isinstance(state.requirement, str)
    assert isinstance(state.plan, str)
    assert isinstance(state.database_code, str)
    assert isinstance(state.backend_code, str)
    assert isinstance(state.frontend_code, str)
    assert isinstance(state.final_report, str)
    assert isinstance(state.project_name, str)
    assert isinstance(state.status, str)


def test_development_state_project_name_optional():
    """Test that project_name field is optional and can be None."""
    state1 = DevelopmentState(project_name=None)
    state2 = DevelopmentState(project_name="TestProject")
    state3 = DevelopmentState()  # Should default to None
    
    assert state1.project_name is None
    assert state2.project_name == "TestProject"
    assert state3.project_name is None


def test_development_state_empty_strings():
    """Test that string fields can be empty strings."""
    state = DevelopmentState(
        requirement="",
        plan="",
        database_code="",
        backend_code="",
        frontend_code="",
        final_report="",
        status=""
    )
    
    assert state.requirement == ""
    assert state.plan == ""
    assert state.database_code == ""
    assert state.backend_code == ""
    assert state.frontend_code == ""
    assert state.final_report == ""
    assert state.status == ""


def test_development_state_model_validation():
    """Test that Pydantic validation works correctly."""
    # Valid state should not raise any exceptions
    state = DevelopmentState(
        requirement="Valid requirement",
        status="valid_status"
    )
    
    assert state.requirement == "Valid requirement"
    assert state.status == "valid_status"


def test_development_state_field_descriptions():
    """Test that field descriptions are properly set in the model."""
    # Access the model fields to check descriptions
    fields = DevelopmentState.__fields__
    
    assert "id" in fields
    assert "requirement" in fields
    assert "plan" in fields
    assert "database_code" in fields
    assert "backend_code" in fields
    assert "frontend_code" in fields
    assert "final_report" in fields
    assert "project_name" in fields
    assert "status" in fields
    
    # Check that descriptions exist
    assert fields["id"].field_info.description is not None
    assert fields["requirement"].field_info.description is not None
    assert fields["plan"].field_info.description is not None


def test_development_state_serialization():
    """Test that DevelopmentState can be serialized to dict."""
    state = DevelopmentState(
        requirement="Test requirement",
        plan="Test plan",
        status="testing"
    )
    
    state_dict = state.dict()
    
    assert isinstance(state_dict, dict)
    assert "id" in state_dict
    assert "requirement" in state_dict
    assert "plan" in state_dict
    assert "database_code" in state_dict
    assert "backend_code" in state_dict
    assert "frontend_code" in state_dict
    assert "final_report" in state_dict
    assert "project_name" in state_dict
    assert "status" in state_dict
    
    assert state_dict["requirement"] == "Test requirement"
    assert state_dict["plan"] == "Test plan"
    assert state_dict["status"] == "testing"


def test_development_state_json_serialization():
    """Test that DevelopmentState can be serialized to JSON."""
    state = DevelopmentState(
        requirement="JSON test",
        status="json_testing"
    )
    
    json_str = state.json()
    
    assert isinstance(json_str, str)
    assert "JSON test" in json_str
    assert "json_testing" in json_str


@pytest.mark.parametrize("field_name,field_value", [
    ("requirement", "Test requirement"),
    ("plan", "Test plan"),
    ("database_code", "SELECT * FROM test;"),
    ("backend_code", "def test(): pass"),
    ("frontend_code", "<div>Test</div>"),
    ("final_report", "Test report"),
    ("project_name", "TestProject"),
    ("status", "test_status")
])
def test_development_state_individual_fields(field_name, field_value):
    """Test that individual fields can be set and retrieved correctly."""
    kwargs = {field_name: field_value}
    state = DevelopmentState(**kwargs)
    
    assert getattr(state, field_name) == field_value