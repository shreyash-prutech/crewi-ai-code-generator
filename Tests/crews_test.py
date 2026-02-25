import os
import sys
import types
from pathlib import Path
import importlib.util
import pytest
from unittest.mock import MagicMock

class ConfigDict(dict):
    def __init__(self):
        super().__init__()
        self.accessed = []

    def __getitem__(self, key):
        self.accessed.append(key)
        return {"name": key, "key": key}

class DummyLLM:
    def __init__(self, model=None, **kwargs):
        self.model = model
        self.kwargs = kwargs

class DummyAgent:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

class DummyTask:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        if args:
            self.config = args[0]
        else:
            self.config = kwargs.get("config")
        self.tools = kwargs.get("tools")

class DummyCrew:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

class DummyProcess:
    sequential = "sequential"

class DummyBaseAgent:
    pass

class FileWriteTool:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

def setup_fake_modules():
    crewai = types.ModuleType("crewai")
    crewai.Agent = DummyAgent
    crewai.Crew = DummyCrew
    crewai.Process = DummyProcess
    crewai.Task = DummyTask
    crewai.LLM = DummyLLM

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
            if original_init:
                original_init(self, *args, **kwargs)
            if isinstance(getattr(self, "agents_config", None), str):
                self.agents_config = ConfigDict()
            if isinstance(getattr(self, "tasks_config", None), str):
                self.tasks_config = ConfigDict()
        cls.__init__ = __init__
        return cls

    project.CrewBase = CrewBase
    project.agent = agent
    project.task = task
    project.crew = crew

    base_agent_mod = types.ModuleType("crewai.agents.agent_builder.base_agent")
    base_agent_mod.BaseAgent = DummyBaseAgent

    dotenv_mod = types.ModuleType("dotenv")
    dotenv_mod.load_dotenv = MagicMock()

    file_write_mod = types.ModuleType("code_genereator.tools.file_write_tool")
    file_write_mod.FileWriteTool = FileWriteTool

    sys.modules["crewai"] = crewai
    sys.modules["crewai.project"] = project
    sys.modules["crewai.agents"] = types.ModuleType("crewai.agents")
    sys.modules["crewai.agents.agent_builder"] = types.ModuleType("crewai.agents.agent_builder")
    sys.modules["crewai.agents.agent_builder.base_agent"] = base_agent_mod
    sys.modules["dotenv"] = dotenv_mod
    sys.modules["code_genereator.tools.file_write_tool"] = file_write_mod
    return dotenv_mod

def import_crews_module(monkeypatch, model_env=None):
    dotenv_mod = setup_fake_modules()
    if model_env is None:
        monkeypatch.delenv("MODEL", raising=False)
    else:
        monkeypatch.setenv("MODEL", model_env)

    for mod_name in list(sys.modules.keys()):
        if mod_name in ("code_genereator.crews", "crews"):
            del sys.modules[mod_name]

    pkg = types.ModuleType("code_genereator")
    pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "src" / "code_genereator")]
    sys.modules["code_genereator"] = pkg

    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "src" / "code_genereator" / "crews.py"
    spec = importlib.util.spec_from_file_location("code_genereator.crews", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["code_genereator.crews"] = module
    spec.loader.exec_module(module)
    return module, dotenv_mod

def exercise_crew_class(module, class_name):
    cls = getattr(module, class_name)
    instance = cls()
    if not hasattr(instance, "agents_config") or isinstance(instance.agents_config, str):
        instance.agents_config = ConfigDict()
    if not hasattr(instance, "tasks_config") or isinstance(instance.tasks_config, str):
        instance.tasks_config = ConfigDict()
    instance.agents = [DummyAgent()]
    instance.tasks = [DummyTask(config={"name": "task"})]
    results = {}
    for name, attr in cls.__dict__.items():
        if callable(attr) and not name.startswith("_"):
            if name == "crew":
                instance.agents = [DummyAgent()]
                instance.tasks = [DummyTask(config={"name": "task"})]
            result = getattr(instance, name)()
            results[name] = result
    return results

def test_import_default_model_and_load_dotenv_called(monkeypatch, capsys):
    """Validate default MODEL selection and load_dotenv invocation during import."""
    module, dotenv_mod = import_crews_module(monkeypatch, model_env=None)
    captured = capsys.readouterr()
    assert module.MODEL == "gpt-4o"
    assert "Using model: gpt-4o" in captured.out
    assert dotenv_mod.load_dotenv.called is True

def test_import_custom_model_overrides_default(monkeypatch, capsys):
    """Validate custom MODEL environment variable overrides the default."""
    module, dotenv_mod = import_crews_module(monkeypatch, model_env="custom-model")
    captured = capsys.readouterr()
    assert module.MODEL == "custom-model"
    assert "Using model: custom-model" in captured.out
    assert dotenv_mod.load_dotenv.called is True

@pytest.mark.parametrize("class_name", ["PlanningCrew", "EngineeringCrew", "JudgeCrew"])
def test_all_crews_methods_return_expected_objects(monkeypatch, class_name):
    """Ensure all crew methods return correct object types and preserve configuration."""
    module, _ = import_crews_module(monkeypatch, model_env="test-model")
    results = exercise_crew_class(module, class_name)
    assert results, "Expected at least one callable method to be exercised"

    for name, result in results.items():
        assert isinstance(result, (DummyAgent, DummyTask, DummyCrew))
        if isinstance(result, DummyAgent):
            llm = result.kwargs.get("llm")
            assert isinstance(llm, DummyLLM)
            assert llm.model == module.MODEL
            config = result.kwargs.get("config")
            assert isinstance(config, dict)
            assert "name" in config
            if "reasoning" in result.kwargs:
                assert result.kwargs["reasoning"] is True
                if "max_reasoning_attempts" in result.kwargs:
                    assert result.kwargs["max_reasoning_attempts"] == 3
        if isinstance(result, DummyTask):
            assert isinstance(result.config, dict)
            assert "name" in result.config
            if result.tools is not None:
                assert all(isinstance(t, FileWriteTool) for t in result.tools)
        if isinstance(result, DummyCrew):
            assert result.kwargs.get("agents") is not None
            assert result.kwargs.get("tasks") is not None
            assert result.kwargs.get("process") == DummyProcess.sequential
            assert result.kwargs.get("verbose") is True
            if "planning" in result.kwargs:
                assert result.kwargs.get("planning") is True

def test_planning_crew_reasoning_configuration(monkeypatch):
    """Specifically validate reasoning configuration for PlanningCrew architect agent."""
    module, _ = import_crews_module(monkeypatch, model_env="reasoning-model")
    planning = module.PlanningCrew()
    planning.agents_config = ConfigDict()
    agent_instance = planning.architect()
    assert isinstance(agent_instance, DummyAgent)
    assert agent_instance.kwargs.get("reasoning") is True
    assert agent_instance.kwargs.get("max_reasoning_attempts") == 3
    llm = agent_instance.kwargs.get("llm")
    assert isinstance(llm, DummyLLM)
    assert llm.model == module.MODEL