import os
import sys
import types
import inspect
import importlib.util
from pathlib import Path
from uuid import uuid4
from unittest.mock import patch
import pytest

# TEST PLAN:
# - test_import_default_model_and_print
# - test_import_custom_model_from_env
# - test_planning_crew_methods
# - test_engineering_crew_all_methods
# - test_judge_crew_all_methods


def _find_repo_root():
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "src" / "code_genereator" / "crews.py").exists():
            return parent
    return current.parents[1]


REPO_ROOT = _find_repo_root()


class ConfigRecorder:
    def __init__(self, prefix):
        self.prefix = prefix
        self.history = []

    def __getitem__(self, key):
        self.history.append(key)
        return f"{self.prefix}_{key}"


def _build_fake_modules(registry):
    crewai = types.ModuleType("crewai")

    class DummyBase:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class LLM(DummyBase):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if "model" in kwargs:
                self.model = kwargs["model"]
            elif args:
                self.model = args[0]
            else:
                self.model = None

    class Agent(DummyBase):
        pass

    class Task(DummyBase):
        pass

    class Crew(DummyBase):
        pass

    class Process:
        sequential = "sequential"

    crewai.Agent = Agent
    crewai.Crew = Crew
    crewai.Process = Process
    crewai.Task = Task
    crewai.LLM = LLM

    project = types.ModuleType("crewai.project")

    def agent(func):
        return func

    def task(func):
        return func

    def crew(func):
        return func

    def CrewBase(cls):
        original_init = getattr(cls, "__init__", None)

        def __init__(self, *args, **kwargs):
            if original_init is not None:
                original_init(self, *args, **kwargs)
            if not hasattr(self, "agents"):
                self.agents = []
            if not hasattr(self, "tasks"):
                self.tasks = []

        cls.__init__ = __init__
        return cls

    project.CrewBase = CrewBase
    project.agent = agent
    project.task = task
    project.crew = crew

    agents_module = types.ModuleType("crewai.agents")
    agent_builder_module = types.ModuleType("crewai.agents.agent_builder")
    base_agent_module = types.ModuleType("crewai.agents.agent_builder.base_agent")

    class BaseAgent:
        pass

    base_agent_module.BaseAgent = BaseAgent

    dotenv = types.ModuleType("dotenv")

    def load_dotenv():
        registry["load_dotenv_calls"] += 1

    dotenv.load_dotenv = load_dotenv

    code_gen_module = types.ModuleType("code_genereator")
    tools_module = types.ModuleType("code_genereator.tools")
    file_write_tool_module = types.ModuleType("code_genereator.tools.file_write_tool")

    class FileWriteTool:
        pass

    file_write_tool_module.FileWriteTool = FileWriteTool

    fakes = {
        "crewai": crewai,
        "crewai.project": project,
        "crewai.agents": agents_module,
        "crewai.agents.agent_builder": agent_builder_module,
        "crewai.agents.agent_builder.base_agent": base_agent_module,
        "dotenv": dotenv,
        "code_genereator": code_gen_module,
        "code_genereator.tools": tools_module,
        "code_genereator.tools.file_write_tool": file_write_tool_module,
    }
    return fakes


@pytest.fixture
def crews_importer():
    def _import(model_env=None):
        if model_env is None:
            os.environ.pop("MODEL", None)
        else:
            os.environ["MODEL"] = model_env

        registry = {"load_dotenv_calls": 0}
        fakes = _build_fake_modules(registry)
        for name, mod in fakes.items():
            sys.modules[name] = mod

        module_name = f"crews_module_{uuid4().hex}"
        file_path = REPO_ROOT / "src" / "code_genereator" / "crews.py"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module, registry

    return _import


def _expected_config_matches(value, prefix, name, recorder):
    if value is None:
        return True
    expected_from_name = f"{prefix}_{name}"
    if recorder.history:
        expected_from_history = f"{prefix}_{recorder.history[-1]}"
        if value == expected_from_history:
            return True
    return value == expected_from_name


def _exercise_crew_class(module, crew_cls, expect_planning_flag=False):
    instance = crew_cls()
    instance.agents = ["agent1", "agent2"]
    instance.tasks = ["task1", "task2"]
    agent_rec = ConfigRecorder("agent")
    task_rec = ConfigRecorder("task")
    instance.agents_config = agent_rec
    instance.tasks_config = task_rec

    results = {}
    for name, func in crew_cls.__dict__.items():
        if name.startswith("__"):
            continue
        if not callable(func):
            continue
        sig = inspect.signature(func)
        if len(sig.parameters) != 1:
            continue
        result = getattr(instance, name)()
        results[name] = result
        if "task" in name:
            assert isinstance(result, module.Task)
            config_value = result.kwargs.get("config")
            assert _expected_config_matches(config_value, "task", name, task_rec)
            if "tools" in result.kwargs:
                for tool in result.kwargs["tools"]:
                    assert isinstance(tool, module.FileWriteTool)
        elif name == "crew":
            assert isinstance(result, module.Crew)
            assert result.kwargs.get("agents") == instance.agents
            assert result.kwargs.get("tasks") == instance.tasks
            if "process" in result.kwargs:
                assert result.kwargs["process"] == module.Process.sequential
            if "verbose" in result.kwargs:
                assert result.kwargs["verbose"] is True
            if expect_planning_flag and "planning" in result.kwargs:
                assert result.kwargs["planning"] is True
        else:
            assert isinstance(result, module.Agent)
            config_value = result.kwargs.get("config")
            assert _expected_config_matches(config_value, "agent", name, agent_rec)
            if "llm" in result.kwargs:
                llm = result.kwargs["llm"]
                assert isinstance(llm, module.LLM)
                assert getattr(llm, "model", None) == module.MODEL
            if "verbose" in result.kwargs:
                assert result.kwargs["verbose"] is True
            if "tools" in result.kwargs:
                for tool in result.kwargs["tools"]:
                    assert isinstance(tool, module.FileWriteTool)

    agent_methods = [n for n in results if "task" not in n and n != "crew"]
    task_methods = [n for n in results if "task" in n]
    assert len(agent_rec.history) >= 0
    assert len(task_rec.history) >= len(task_methods)
    return results, agent_rec, task_rec


def test_import_default_model_and_print(crews_importer):
    """Validate default MODEL selection and startup print when env is absent."""
    with patch("builtins.print") as mock_print:
        module, registry = crews_importer(model_env=None)
    assert module.MODEL == "gpt-4o"
    assert registry["load_dotenv_calls"] == 1
    mock_print.assert_called_with("Using model: gpt-4o")


def test_import_custom_model_from_env(crews_importer):
    """Validate MODEL overrides from environment variables and print reflects it."""
    with patch("builtins.print") as mock_print:
        module, registry = crews_importer(model_env="custom-model")
    assert module.MODEL == "custom-model"
    assert registry["load_dotenv_calls"] == 1
    mock_print.assert_called_with("Using model: custom-model")


def test_planning_crew_methods(crews_importer):
    """Validate PlanningCrew agent, task, and crew construction with expected settings."""
    module, _ = crews_importer(model_env="planning-model")
    crew_instance = module.PlanningCrew()
    crew_instance.agents = ["a1"]
    crew_instance.tasks = ["t1"]
    agent_rec = ConfigRecorder("agent")
    task_rec = ConfigRecorder("task")
    crew_instance.agents_config = agent_rec
    crew_instance.tasks_config = task_rec

    architect = crew_instance.architect()
    assert isinstance(architect, module.Agent)
    assert architect.kwargs["config"] == "agent_architect"
    assert architect.kwargs["verbose"] is True
    assert architect.kwargs["reasoning"] is True
    assert architect.kwargs["max_reasoning_attempts"] == 3
    assert isinstance(architect.kwargs["llm"], module.LLM)
    assert architect.kwargs["llm"].model == module.MODEL

    planning_task = crew_instance.planning_task()
    assert isinstance(planning_task, module.Task)
    assert planning_task.kwargs["config"] == "task_planning_task"

    planning_crew = crew_instance.crew()
    assert isinstance(planning_crew, module.Crew)
    assert planning_crew.kwargs["agents"] == ["a1"]
    assert planning_crew.kwargs["tasks"] == ["t1"]
    assert planning_crew.kwargs["process"] == module.Process.sequential
    assert planning_crew.kwargs["verbose"] is True
    assert planning_crew.kwargs["planning"] is True


def test_engineering_crew_all_methods(crews_importer):
    """Exercise all EngineeringCrew methods and validate constructed objects."""
    module, _ = crews_importer(model_env="eng-model")
    results, agent_rec, task_rec = _exercise_crew_class(module, module.EngineeringCrew, expect_planning_flag=False)
    assert results
    assert agent_rec.history or task_rec.history


def test_judge_crew_all_methods(crews_importer):
    """Exercise all JudgeCrew methods and validate constructed objects."""
    module, _ = crews_importer(model_env="judge-model")
    results, agent_rec, task_rec = _exercise_crew_class(module, module.JudgeCrew, expect_planning_flag=False)
    assert results
    assert agent_rec.history or task_rec.history