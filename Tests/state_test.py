# QIF_AUTOGEN_MARKER_v1
import importlib.util
import sys
import uuid
from pathlib import Path
from unittest.mock import Mock

import pytest
from pydantic import ValidationError


try:
    from code_genereator import state as state_module
except Exception:
    REPO_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location(
        "state_module_under_test",
        REPO_ROOT / "src" / "code_genereator" / "state.py",
    )
    state_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(state_module)

DevelopmentState = state_module.DevelopmentState


def _model_to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _model_to_json(model):
    if hasattr(model, "model_dump_json"):
        return model.model_dump_json()
    return model.json()


def _model_copy(model, **kwargs):
    if hasattr(model, "model_copy"):
        return model.model_copy(**kwargs)
    return model.copy(**kwargs)


def _model_fields(model_cls):
    if hasattr(model_cls, "model_fields"):
        return model_cls.model_fields
    return model_cls.__fields__


def _field_default(field):
    if hasattr(field, "default"):
        return field.default
    return field.get_default()


def _field_description(field):
    if hasattr(field, "description"):
        return field.description
    return field.field_info.description


def test_development_state_imports_real_source_class():
    """Validates that the real DevelopmentState class from the source module can be imported and instantiated."""
    state = DevelopmentState()
    assert isinstance(state, DevelopmentState)
    assert state.__class__.__name__ == "DevelopmentState"
    assert state_module.__file__.endswith("state.py")


def test_development_state_default_values():
    """Validates all default values populated by the real Pydantic model."""
    state = DevelopmentState()

    assert isinstance(state.id, str)
    assert uuid.UUID(state.id).version == 4
    assert state.requirement == ""
    assert state.plan == ""
    assert state.database_code == ""
    assert state.backend_code == ""
    assert state.frontend_code == ""
    assert state.final_report == ""
    assert state.project_name is None
    assert state.status == "initialized"


def test_development_state_generates_unique_ids_for_each_instance():
    """Validates that the UUID default factory runs separately for each new state."""
    first = DevelopmentState()
    second = DevelopmentState()

    assert first.id != second.id
    assert uuid.UUID(first.id)
    assert uuid.UUID(second.id)


def test_development_state_uuid_default_factory_uses_module_uuid4(monkeypatch):
    """Validates that the id default factory calls uuid.uuid4 from the production module."""
    fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
    uuid4_mock = Mock(return_value=fixed_uuid)

    monkeypatch.setattr(state_module.uuid, "uuid4", uuid4_mock)

    state = DevelopmentState()

    uuid4_mock.assert_called_once_with()
    assert state.id == str(fixed_uuid)


def test_development_state_accepts_all_custom_field_values():
    """Validates explicit initialization for every field on the state model."""
    state = DevelopmentState(
        id="flow-001",
        requirement="Build a task manager",
        plan="Use FastAPI, PostgreSQL, and React",
        database_code="CREATE TABLE tasks (id INTEGER PRIMARY KEY);",
        backend_code="from fastapi import FastAPI",
        frontend_code="export default function App() {}",
        final_report="All checks passed",
        project_name="Task Manager",
        status="completed",
    )

    assert state.id == "flow-001"
    assert state.requirement == "Build a task manager"
    assert state.plan == "Use FastAPI, PostgreSQL, and React"
    assert state.database_code == "CREATE TABLE tasks (id INTEGER PRIMARY KEY);"
    assert state.backend_code == "from fastapi import FastAPI"
    assert state.frontend_code == "export default function App() {}"
    assert state.final_report == "All checks passed"
    assert state.project_name == "Task Manager"
    assert state.status == "completed"


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("id", "custom-id"),
        ("requirement", "custom requirement"),
        ("plan", "custom plan"),
        ("database_code", "custom database code"),
        ("backend_code", "custom backend code"),
        ("frontend_code", "custom frontend code"),
        ("final_report", "custom final report"),
        ("project_name", "custom project"),
        ("status", "custom status"),
    ],
)
def test_development_state_accepts_individual_custom_values(field_name, value):
    """Validates that each individual field can be supplied without affecting unrelated defaults."""
    state = DevelopmentState(**{field_name: value})

    assert getattr(state, field_name) == value
    if field_name != "id":
        assert isinstance(state.id, str)
        assert uuid.UUID(state.id)
    if field_name != "status":
        assert state.status == "initialized"


def test_development_state_accepts_empty_strings_for_text_fields():
    """Validates that empty strings are accepted for all string fields."""
    state = DevelopmentState(
        id="",
        requirement="",
        plan="",
        database_code="",
        backend_code="",
        frontend_code="",
        final_report="",
        project_name="",
        status="",
    )

    assert state.id == ""
    assert state.requirement == ""
    assert state.plan == ""
    assert state.database_code == ""
    assert state.backend_code == ""
    assert state.frontend_code == ""
    assert state.final_report == ""
    assert state.project_name == ""
    assert state.status == ""


def test_development_state_accepts_none_for_optional_project_name():
    """Validates that project_name is optional and accepts None explicitly."""
    state = DevelopmentState(project_name=None)

    assert state.project_name is None


@pytest.mark.parametrize(
    "field_name",
    [
        "id",
        "requirement",
        "plan",
        "database_code",
        "backend_code",
        "frontend_code",
        "final_report",
        "status",
    ],
)
def test_development_state_rejects_none_for_required_string_fields(field_name):
    """Validates validation errors when non-optional string fields receive None."""
    with pytest.raises(ValidationError):
        DevelopmentState(**{field_name: None})


def test_development_state_ignores_unknown_extra_fields_by_default():
    """Validates Pydantic BaseModel default behavior for unknown fields."""
    state = DevelopmentState(requirement="Known", unknown_field="ignored")

    assert state.requirement == "Known"
    assert not hasattr(state, "unknown_field")
    assert "unknown_field" not in _model_to_dict(state)


def test_development_state_serializes_to_dict_with_expected_keys_and_values():
    """Validates dictionary serialization contains the complete state payload."""
    state = DevelopmentState(
        id="flow-123",
        requirement="Requirement",
        plan="Plan",
        database_code="DB",
        backend_code="Backend",
        frontend_code="Frontend",
        final_report="Report",
        project_name="Project",
        status="running",
    )

    data = _model_to_dict(state)

    assert data == {
        "id": "flow-123",
        "requirement": "Requirement",
        "plan": "Plan",
        "database_code": "DB",
        "backend_code": "Backend",
        "frontend_code": "Frontend",
        "final_report": "Report",
        "project_name": "Project",
        "status": "running",
    }


def test_development_state_serializes_to_json():
    """Validates JSON serialization includes all model fields."""
    state = DevelopmentState(
        id="flow-json",
        requirement="Req",
        plan="Plan",
        database_code="DB",
        backend_code="BE",
        frontend_code="FE",
        final_report="Done",
        project_name=None,
        status="validated",
    )

    json_payload = _model_to_json(state)

    assert '"id"' in json_payload
    assert '"flow-json"' in json_payload
    assert '"requirement"' in json_payload
    assert '"Req"' in json_payload
    assert '"project_name"' in json_payload
    assert "null" in json_payload
    assert '"status"' in json_payload
    assert '"validated"' in json_payload


def test_development_state_copy_update_preserves_original_and_updates_copy():
    """Validates Pydantic copy/update behavior for state transitions."""
    original = DevelopmentState(requirement="Initial requirement", status="initialized")

    updated = _model_copy(
        original,
        update={
            "plan": "Generated plan",
            "status": "planned",
        },
    )

    assert original.requirement == "Initial requirement"
    assert original.plan == ""
    assert original.status == "initialized"
    assert updated.id == original.id
    assert updated.requirement == "Initial requirement"
    assert updated.plan == "Generated plan"
    assert updated.status == "planned"


def test_development_state_field_names_match_expected_model_contract():
    """Validates the model exposes exactly the expected fields."""
    fields = _model_fields(DevelopmentState)

    assert list(fields.keys()) == [
        "id",
        "requirement",
        "plan",
        "database_code",
        "backend_code",
        "frontend_code",
        "final_report",
        "project_name",
        "status",
    ]


@pytest.mark.parametrize(
    "field_name,expected_default",
    [
        ("requirement", ""),
        ("plan", ""),
        ("database_code", ""),
        ("backend_code", ""),
        ("frontend_code", ""),
        ("final_report", ""),
        ("project_name", None),
        ("status", "initialized"),
    ],
)
def test_development_state_field_defaults(field_name, expected_default):
    """Validates declared Field defaults for all non-factory fields."""
    fields = _model_fields(DevelopmentState)

    assert _field_default(fields[field_name]) == expected_default


def test_development_state_id_field_has_default_factory():
    """Validates that id is generated by a default factory rather than a static value."""
    fields = _model_fields(DevelopmentState)
    id_field = fields["id"]

    default_factory = getattr(id_field, "default_factory", None)
    if default_factory is None and hasattr(id_field, "field_info"):
        default_factory = id_field.field_info.default_factory

    assert default_factory is not None
    generated = default_factory()
    assert isinstance(generated, str)
    assert uuid.UUID(generated)


@pytest.mark.parametrize(
    "field_name,expected_description",
    [
        ("id", "Unique identifier for the flow execution"),
        ("requirement", "The original software requirement or feature request"),
        ("plan", "Technical specification/plan generated by the Architect"),
        ("database_code", "SQL schemas, ORM models, and database-related code"),
        ("backend_code", "API endpoints, business logic, and backend services"),
        ("frontend_code", "UI components, pages, and frontend logic"),
        ("final_report", "Final audit report with integrated code and validation results"),
        ("project_name", "Extracted project name from the requirement"),
        ("status", "Current status of the development flow"),
    ],
)
def test_development_state_field_descriptions(field_name, expected_description):
    """Validates Field descriptions used as model metadata."""
    fields = _model_fields(DevelopmentState)

    assert _field_description(fields[field_name]) == expected_description


def test_development_state_model_dump_round_trip():
    """Validates a serialized state can be used to reconstruct an equivalent state."""
    original = DevelopmentState(
        id="round-trip-id",
        requirement="Make an API",
        plan="Design API",
        database_code="schema",
        backend_code="service",
        frontend_code="client",
        final_report="ok",
        project_name="API Project",
        status="done",
    )

    reconstructed = DevelopmentState(**_model_to_dict(original))

    assert reconstructed == original
    assert _model_to_dict(reconstructed) == _model_to_dict(original)