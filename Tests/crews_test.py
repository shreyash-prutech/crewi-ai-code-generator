import sys
import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CREWS_PATH = REPO_ROOT / "src" / "code_genereator" / "crews.py"


def import_crews_module(monkeypatch, model_env=None):
    for name in list(sys.modules):
        if name == "code_genereator.crews" or name.startswith("crewai") or name.startswith("code_genereator") or name == "dotenv":
            sys.modules.pop(name, None)

    if model_env is None:
        monkeypatch.delenv("MODEL", raising=False)
    else:
        monkeypatch.setenv("MODEL", model_env)

    crewai = ModuleType("crewai")
    Agent = MagicMock(name="Agent")
    Crew = MagicMock(name="Crew")
    Task = MagicMock(name="Task")
    LLM = MagicMock(name="LLM")
    Process = SimpleNamespace(sequential="sequential")
    crewai.Agent = Agent
    crewai.Crew = Crew
    crewai.Task = Task
    crewai.LLM = LLM
    crewai.Process = Process

    project = ModuleType("crewai.project")

    def identity_decorator(func):
        return func

    def CrewBase(cls):
        return cls

    project.CrewBase = CrewBase
    project.agent = identity_decorator
    project.task = identity_decorator
    project.crew = identity_decorator

    agents_pkg = ModuleType("crewai.agents")
    agents_pkg.__path__ = []
    agent_builder_pkg = ModuleType("crewai.agents.agent_builder")
    agent_builder_pkg.__path__ = []
    base_agent_module = ModuleType("crewai.agents.agent_builder.base_agent")

    class BaseAgent:
        pass

    base_agent_module.BaseAgent = BaseAgent

    dotenv = ModuleType("dotenv")
    load_dotenv = MagicMock(name="load_dotenv")
    dotenv.load_dotenv = load_dotenv

    code_genereator_pkg = ModuleType("code_genereator")
    code_genereator_pkg.__path__ = []
    tools_pkg = ModuleType("code_genereator.tools")
    tools_pkg.__path__ = []
    file_write_tool_module = ModuleType("code_genereator.tools.file_write_tool")

    class FileWriteTool:
        pass

    file_write_tool_module.FileWriteTool = FileWriteTool

    monkeypatch.setitem(sys.modules, "crewai", crewai)
    monkeypatch.setitem(sys.modules, "crewai.project", project)
    monkeypatch.setitem(sys.modules, "crewai.agents", agents_pkg)
    monkeypatch.setitem(sys.modules, "crewai.agents.agent_builder", agent_builder_pkg)
    monkeypatch.setitem(sys.modules, "crewai.agents.agent_builder.base_agent", base_agent_module)
    monkeypatch.setitem(sys.modules, "dotenv", dotenv)
    monkeypatch.setitem(sys.modules, "code_genereator", code_genereator_pkg)
    monkeypatch.setitem(sys.modules, "code_genereator.tools", tools_pkg)
    monkeypatch.setitem(sys.modules, "code_genereator.tools.file_write_tool", file_write_tool_module)

    spec = importlib.util.spec_from_file_location("code_genereator.crews", CREWS_PATH)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "code_genereator.crews", module)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    mocks = {
        "Agent": Agent,
        "Crew": Crew,
        "Task": Task,
        "LLM": LLM,
        "Process": Process,
        "load_dotenv": load_dotenv,
    }
    return module, mocks


def test_default_model_and_load_dotenv(monkeypatch, capsys):
    """Validates default model and dotenv loading when MODEL is not set."""
    module, mocks = import_crews_module(monkeypatch)
    captured = capsys.readouterr().out
    assert module.MODEL == "gpt-4o"
    assert mocks["load_dotenv"].called
    assert "Using model: gpt-4o" in captured


def test_custom_model_env(monkeypatch, capsys):
    """Ensures custom model environment variable overrides default."""
    module, mocks = import_crews_module(monkeypatch, model_env="custom-model")
    captured = capsys.readouterr().out
    assert module.MODEL == "custom-model"
    assert mocks["load_dotenv"].called
    assert "Using model: custom-model" in captured


def test_planningcrew_happy_path(monkeypatch):
    """Validates PlanningCrew agent, task, and crew creation behaviors."""
    module, mocks = import_crews_module(monkeypatch, model_env="unit-model")
    crew_instance = module.PlanningCrew()
    crew_instance.agents_config = {"architect": {"role": "architect"}}
    crew_instance.tasks_config = {"planning_task": {"task": "plan"}}
    crew_instance.agents = ["agent1"]
    crew_instance.tasks = ["task1"]

    agent = crew_instance.architect()
    assert agent == mocks["Agent"].return_value
    mocks["LLM"].assert_called_with(model=module.MODEL)
    agent_kwargs = mocks["Agent"].call_args.kwargs
    assert agent_kwargs["config"] == crew_instance.agents_config["architect"]
    assert agent_kwargs["verbose"] is True
    assert agent_kwargs["llm"] == mocks["LLM"].return_value
    assert agent_kwargs["reasoning"] is True
    assert agent_kwargs["max_reasoning_attempts"] == 3

    task = crew_instance.planning_task()
    assert task == mocks["Task"].return_value
    task_kwargs = mocks["Task"].call_args.kwargs
    assert task_kwargs["config"] == crew_instance.tasks_config["planning_task"]

    crew_obj = crew_instance.crew()
    assert crew_obj == mocks["Crew"].return_value
    crew_kwargs = mocks["Crew"].call_args.kwargs
    assert crew_kwargs["agents"] == crew_instance.agents
    assert crew_kwargs["tasks"] == crew_instance.tasks
    assert crew_kwargs["process"] == mocks["Process"].sequential
    assert crew_kwargs["verbose"] is True
    assert crew_kwargs["planning"] is True


@pytest.mark.parametrize("attr, method_name", [("agents_config", "architect"), ("tasks_config", "planning_task")])
def test_planningcrew_invalid_configs_raise(monkeypatch, attr, method_name):
    """Ensures invalid configuration types raise TypeError in PlanningCrew methods."""
    module, _ = import_crews_module(monkeypatch)
    crew_instance = module.PlanningCrew()
    setattr(crew_instance, attr, None)
    with pytest.raises(TypeError):
        getattr(crew_instance, method_name)()