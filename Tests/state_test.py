import sys
import uuid
from pathlib import Path
import importlib.util
from unittest.mock import MagicMock
import pytest
from pydantic import ValidationError

try:
    from code_genereator.state import DevelopmentState
except Exception:
    REPO_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location(
        "state", REPO_ROOT / "src" / "code_genereator" / "state.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    DevelopmentState = module.DevelopmentState


def test_default_state_values_and_uuid():
    """Validate that the default state initializes all fields and generates a UUID."""
    state = DevelopmentState()
    assert isinstance(state.id, str)
    assert state.id
    uuid_obj = uuid.UUID(state.id)
    assert str(uuid_obj) == state.id
    assert state.requirement == ""
    assert state.plan == ""
    assert state.database_code == ""
    assert state.backend_code == ""
    assert state.frontend_code == ""
    assert state.final_report == ""
    assert state.project_name is None
    assert state.status == "initialized"


@pytest.mark.parametrize(
    "project_name,status",
    [
        ("MyProject", "planning"),
        (None, "engineering"),
    ],
)
def test_state_custom_values(project_name, status):
    """Validate that custom values are preserved through model creation."""
    state = DevelopmentState(
        requirement="Build a service",
        plan="Step 1",
        database_code="CREATE TABLE",
        backend_code="def api(): pass",
        frontend_code="<div/>",
        final_report="All good",
        project_name=project_name,
        status=status,
        id="fixed-id"
    )
    assert state.id == "fixed-id"
    assert state.requirement == "Build a service"
    assert state.plan == "Step 1"
    assert state.database_code == "CREATE TABLE"
    assert state.backend_code == "def api(): pass"
    assert state.frontend_code == "<div/>"
    assert state.final_report == "All good"
    assert state.project_name == project_name
    assert state.status == status


def test_validation_error_on_none_requirement():
    """Validate that None for a required string field raises a validation error."""
    with pytest.raises(ValidationError):
        DevelopmentState(requirement=None)


def test_mock_id_is_coerced_to_string():
    """Validate that non-string id values are coerced to string using MagicMock."""
    mock_id = MagicMock()
    mock_id.__str__.return_value = "mock-id"
    state = DevelopmentState(id=mock_id)
    assert state.id == "mock-id"