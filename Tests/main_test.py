import os
import sys
import types
import builtins
import importlib
import importlib.util
from pathlib import Path
from datetime import datetime as real_datetime
from types import SimpleNamespace
from unittest.mock import mock_open, MagicMock
import pytest


def _install_dummy_crewai():
    if "crewai" in sys.modules:
        return
    crewai_mod = types.ModuleType("crewai")
    flow_mod = types.ModuleType("crewai.flow")
    flow_flow_mod = types.ModuleType("crewai.flow.flow")

    class Flow:
        def __class_getitem__(cls, item):
            return cls

    def listen(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def start(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    flow_flow_mod.Flow = Flow
    flow_flow_mod.listen = listen
    flow_flow_mod.start = start
    sys.modules["crewai"] = crewai_mod
    sys.modules["crewai.flow"] = flow_mod
    sys.modules["crewai.flow.flow"] = flow_flow_mod


@pytest.fixture
def main_module():
    _install_dummy_crewai()
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    try:
        return importlib.import_module("code_genereator.main")
    except Exception:
        spec = importlib.util.spec_from_file_location(
            "code_genereator.main", repo_root / "src" / "code_genereator" / "main.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def _fixed_datetime_class():
    class FixedDateTime:
        @classmethod
        def now(cls):
            return real_datetime(2024, 1, 2, 3, 4, 5)
    return FixedDateTime


def _make_state(**overrides):
    base = dict(
        id="flow-123",
        status="COMPLETED",
        requirement="Build a system",
        plan="Use layered architecture",
        database_code="CREATE TABLE users(id INT);",
        backend_code="print('backend')",
        frontend_code="<div>frontend</div>",
        final_report="All good"
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_save_execution_log_happy_path(main_module, tmp_path, monkeypatch):
    """Validate that save_execution_log writes the expected log content and returns correct path."""
    fake_file = tmp_path / "a" / "b" / "c" / "main.py"
    monkeypatch.setattr(main_module, "__file__", str(fake_file))
    monkeypatch.setattr(main_module, "datetime", _fixed_datetime_class())
    m = mock_open()
    monkeypatch.setattr(builtins, "open", m)

    state = _make_state()
    log_file = main_module.save_execution_log(state)

    expected_base = tmp_path / "a"
    expected_log = expected_base / "dist" / "logs" / "execution_log_20240102_030405.md"
    assert log_file == str(expected_log)

    written = m().write.call_args[0][0]
    assert state.requirement in written
    assert state.plan in written
    assert state.database_code in written
    assert state.backend_code in written
    assert state.frontend_code in written
    assert state.final_report in written
    assert "✅" in written
    assert "Execution Log" in written


@pytest.mark.parametrize(
    "plan,db,backend,frontend,report,expected_marks",
    [
        ("", "", "", "", "", "❌"),
        ("plan", "", "code", "", "report", "✅"),
    ],
)
def test_save_execution_log_edge_cases(main_module, tmp_path, monkeypatch, plan, db, backend, frontend, report, expected_marks):
    """Validate handling of empty artifacts and summary markers in log content."""
    fake_file = tmp_path / "root" / "x" / "y" / "main.py"
    monkeypatch.setattr(main_module, "__file__", str(fake_file))
    monkeypatch.setattr(main_module, "datetime", _fixed_datetime_class())
    m = mock_open()
    monkeypatch.setattr(builtins, "open", m)

    state = _make_state(
        plan=plan,
        database_code=db,
        backend_code=backend,
        frontend_code=frontend,
        final_report=report,
    )
    main_module.save_execution_log(state)

    written = m().write.call_args[0][0]
    assert "Summary" in written
    assert expected_marks in written
    assert f"| Plan | {'✅' if plan else '❌'} | {len(plan)} chars |" in written
    assert f"| Database Code | {'✅' if db else '❌'} | {len(db)} chars |" in written
    assert f"| Backend Code | {'✅' if backend else '❌'} | {len(backend)} chars |" in written
    assert f"| Frontend Code | {'✅' if frontend else '❌'} | {len(frontend)} chars |" in written
    assert f"| Final Report | {'✅' if report else '❌'} | {len(report)} chars |" in written


def test_save_execution_log_raises_on_open_error(main_module, tmp_path, monkeypatch):
    """Ensure errors from open propagate when file writing fails."""
    fake_file = tmp_path / "root" / "x" / "y" / "main.py"
    monkeypatch.setattr(main_module, "__file__", str(fake_file))
    monkeypatch.setattr(main_module, "datetime", _fixed_datetime_class())

    def raise_io(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(builtins, "open", raise_io)
    state = _make_state()

    with pytest.raises(OSError):
        main_module.save_execution_log(state)