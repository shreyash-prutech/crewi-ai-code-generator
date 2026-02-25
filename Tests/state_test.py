import sys
import uuid
from pathlib import Path
from unittest.mock import patch
import pytest
from pydantic import ValidationError

try:
    from code_genereator.state import DevelopmentState
    import code_genereator.state as state_module
except Exception:
    import importlib.util
    REPO_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location(
        "state_module", REPO_ROOT / "src/code_genereator/state.py"
    )
    state_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(state_module)
    DevelopmentState = state_module.DevelopmentState


def _model_to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def test_default_values_and_types():
    """Validate default values and generated UUID for a new DevelopmentState."""
    state = DevelopmentState()
    data = _model_to_dict(state)

    assert isinstance(state.id, str)
    # Ensure the ID is a valid UUID string
    assert uuid.UUID(state.id)
    assert state.requirement == ""
    assert state.plan == ""
    assert state.database_code == ""
    assert state.backend_code == ""
    assert state.frontend_code == ""
    assert state.final_report == ""
    assert state.project_name is None
    assert state.status == "initialized"

    # Ensure defaults appear in dict representation
    assert data["requirement"] == ""
    assert data["project_name"] is None
    assert data["status"] == "initialized"


def test_uuid_default_factory_patched():
    """Ensure UUID default factory uses uuid.uuid4 and result is stringified."""
    fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
    with patch.object(state_module.uuid, "uuid4", return_value=fixed_uuid) as mocked:
        state = DevelopmentState()
        assert mocked.called
        assert state.id == str(fixed_uuid)


def test_custom_values_are_set():
    """Validate that providing values sets all fields correctly."""
    state = DevelopmentState(
        requirement="Build a system",
        plan="A detailed plan",
        database_code="CREATE TABLE test;",
        backend_code="def handler(): pass",
        frontend_code="<div>UI</div>",
        final_report="All checks passed",
        project_name="TestProject",
        status="completed",
    )
    assert state.requirement == "Build a system"
    assert state.plan == "A detailed plan"
    assert state.database_code == "CREATE TABLE test;"
    assert state.backend_code == "def handler(): pass"
    assert state.frontend_code == "<div>UI</div>"
    assert state.final_report == "All checks passed"
    assert state.project_name == "TestProject"
    assert state.status == "completed"


@pytest.mark.parametrize("field_name", ["requirement", "status", "id"])
def test_none_for_required_string_fields_raises(field_name):
    """Ensure None for required string fields triggers validation error."""
    kwargs = {field_name: None}
    with pytest.raises(ValidationError):
        DevelopmentState(**kwargs)


def test_project_name_optional_allows_none_and_string():
    """Verify project_name supports both None and string values."""
    state_none = DevelopmentState(project_name=None)
    assert state_none.project_name is None

    state_str = DevelopmentState(project_name="OptionalProject")
    assert state_str.project_name == "OptionalProject"