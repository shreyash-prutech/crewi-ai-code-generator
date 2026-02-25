import sys
import types
import inspect
import importlib
import importlib.util
from pathlib import Path
import pytest

# TEST PLAN:
# 1. Ensure load_dotenv is invoked during module import.
# 2. Validate default model value when MODEL env is not set.
# 3. Validate model value when MODEL env is set.
# 4. Validate PlanningCrew architect agent uses reasoning and LLM model.
# 5. Ensure missing config raises KeyError in architect.
# 6. Ensure missing config raises KeyError in planning_task.
# 7. Validate all agent methods return Agent with config and LLM.
# 8. Validate all task methods return Task with config.
# 9. Validate crew methods return Crew with proper attributes.

class DefaultConfig(dict):
    def __init__(self):
        super().__init__()
        self.last_key = None

    def __getitem__(self, key):
        self.last_key = key
        value = {"key": key}
        super().__setitem__(key, value)
        return value


def install_mock_modules():
    dotenv_mod = types.ModuleType("dotenv")
    dotenv_mod.loaded = False

    def load_dotenv():
        dotenv_mod.loaded = True
        return True

    dotenv_mod.load_dotenv = load_dotenv
    sys.modules["dotenv"] = dotenv_mod

    crewai_mod = types.ModuleType("crewai")

    class LLM:
        def __init__(self, model):
            self.model = model

    class Agent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class Task:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class Crew:
        def __init__(self, agents, tasks, process=None, verbose=None, planning=False):
            self.agents = agents
            self.tasks = tasks
            self.process = process
            self.verbose = verbose
            self.planning = planning

    class Process:
        sequential = "sequential"

    crewai_mod.Agent = Agent
    crewai_mod.Crew = Crew
    crewai_mod.Process = Process
    crewai_mod.Task = Task
    crewai_mod.LLM = LLM
    sys.modules["crewai"] = crewai_mod

    project_mod = types.ModuleType("crewai.project")

    def CrewBase(cls):
        return cls

    def agent(func):
        return func

    def task(func):
        return func

    def crew(func):
        return func

    project_mod.CrewBase = CrewBase
    project_mod.agent = agent
    project_mod.task = task
    project_mod.crew = crew
    sys.modules["crewai.project"] = project_mod
    crewai_mod.project = project_mod

    agents_mod = types.ModuleType("crewai.agents")
    agent_builder_mod = types.ModuleType("crewai.agents.agent_builder")
    base_agent_mod = types.ModuleType("crewai.agents.agent_builder.base_agent")

    class BaseAgent:
        pass

    base_agent_mod.BaseAgent = BaseAgent
    sys.modules["crewai.agents"] = agents_mod
    sys.modules["crewai.agents.agent_builder"] = agent_builder_mod
    sys.modules["crewai.agents.agent_builder.base_agent"] = base_agent_mod
    crewai_mod.agents = agents_mod

    file_write_tool_mod = types.ModuleType("code_genereator.tools.file_write_tool")

    class FileWriteTool:
        pass

    file_write_tool_mod.FileWriteTool = FileWriteTool
    sys.modules["code_genereator.tools.file_write_tool"] = file_write_tool_mod

    if "code_genereator.tools" not in sys.modules:
        tools_pkg = types.ModuleType("code_genereator.tools")
        tools_pkg.__path__ = []
        sys.modules["code_genereator.tools"] = tools_pkg


def import_crews_module(monkeypatch, env_value):
    install_mock_modules()
    if env_value is None:
        monkeypatch.delenv("MODEL", raising=False)
    else:
        monkeypatch.setenv("MODEL", env_value)

    module_name = "code_genereator.crews"
    sys.modules.pop(module_name, None)
    sys.modules.pop("module_under_test", None)

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    try:
        return importlib.import_module(module_name)
    except Exception:
        spec = importlib.util.spec_from_file_location("module_under_test", repo_root / "src/code_genereator/crews.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules["module_under_test"] = module
        spec.loader.exec_module(module)
        return module


def iter_methods_by_return(cls, return_type):
    for name, func in cls.__dict__.items():
        if callable(func) and getattr(func, "__annotations__", {}).get("return") == return_type:
            sig = inspect.signature(func)
            if len(sig.parameters) == 1:
                yield name, func


def test_load_dotenv_called_on_import(monkeypatch):
    """Ensure load_dotenv is invoked during module import."""
    module = import_crews_module(monkeypatch, "model-a")
    assert sys.modules["dotenv"].loaded is True
    assert module is not None


def test_model_default_when_env_missing(monkeypatch):
    """Validate default model value when MODEL env is not set."""
    module = import_crews_module(monkeypatch, None)
    assert module.MODEL == "gpt-4o"


def test_model_from_env(monkeypatch):
    """Validate model value when MODEL env is set."""
    module = import_crews_module(monkeypatch, "custom-model")
    assert module.MODEL == "custom-model"


def test_planning_architect_reasoning_and_llm(monkeypatch):
    """Validate PlanningCrew architect agent uses reasoning and LLM model."""
    module = import_crews_module(monkeypatch, "reasoning-model")
    crew_instance = module.PlanningCrew()
    crew_instance.agents_config = DefaultConfig()
    agent_obj = crew_instance.architect()
    assert isinstance(agent_obj, module.Agent)
    assert agent_obj.kwargs["reasoning"] is True
    assert agent_obj.kwargs["max_reasoning_attempts"] == 3
    assert isinstance(agent_obj.kwargs["llm"], module.LLM)
    assert agent_obj.kwargs["llm"].model == module.MODEL
    assert agent_obj.kwargs["config"]["key"] == crew_instance.agents_config.last_key


def test_planning_architect_missing_config_raises(monkeypatch):
    """Ensure missing config raises KeyError in architect."""
    module = import_crews_module(monkeypatch, "model-x")
    crew_instance = module.PlanningCrew()
    crew_instance.agents_config = {}
    with pytest.raises(KeyError):
        crew_instance.architect()


def test_planning_task_missing_config_raises(monkeypatch):
    """Ensure missing config raises KeyError in planning_task."""
    module = import_crews_module(monkeypatch, "model-x")
    crew_instance = module.PlanningCrew()
    crew_instance.tasks_config = {}
    with pytest.raises(KeyError):
        crew_instance.planning_task()


def test_agent_methods_across_crews(monkeypatch):
    """Validate all agent methods return Agent with config and LLM."""
    module = import_crews_module(monkeypatch, "agent-model")
    for cls in [module.PlanningCrew, module.EngineeringCrew, module.JudgeCrew]:
        for name, func in iter_methods_by_return(cls, module.Agent):
            instance = cls()
            instance.agents_config = DefaultConfig()
            agent_obj = func(instance)
            assert isinstance(agent_obj, module.Agent)
            assert "config" in agent_obj.kwargs
            assert agent_obj.kwargs["config"]["key"] == instance.agents_config.last_key
            if "llm" in agent_obj.kwargs:
                assert isinstance(agent_obj.kwargs["llm"], module.LLM)
                assert agent_obj.kwargs["llm"].model == module.MODEL
            if "verbose" in agent_obj.kwargs:
                assert agent_obj.kwargs["verbose"] is True


def test_task_methods_across_crews(monkeypatch):
    """Validate all task methods return Task with config."""
    module = import_crews_module(monkeypatch, "task-model")
    for cls in [module.PlanningCrew, module.EngineeringCrew, module.JudgeCrew]:
        for name, func in iter_methods_by_return(cls, module.Task):
            instance = cls()
            instance.tasks_config = DefaultConfig()
            task_obj = func(instance)
            assert isinstance(task_obj, module.Task)
            assert "config" in task_obj.kwargs
            config_key = task_obj.kwargs["config"]["key"]
            assert config_key in instance.tasks_config


def test_crew_methods_create_crew(monkeypatch):
    """Validate crew methods return Crew with proper attributes."""
    module = import_crews_module(monkeypatch, "crew-model")
    for cls in [module.PlanningCrew, module.EngineeringCrew, module.JudgeCrew]:
        instance = cls()
        instance.agents = ["agent"]
        instance.tasks = ["task"]
        crew_obj = cls.crew(instance)
        assert isinstance(crew_obj, module.Crew)
        assert crew_obj.agents == instance.agents
        assert crew_obj.tasks == instance.tasks
        assert crew_obj.process == module.Process.sequential
        if crew_obj.verbose is not None:
            assert crew_obj.verbose is True
        if cls is module.PlanningCrew:
            assert crew_obj.planning is True