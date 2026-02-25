import sys
import types
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest


def _find_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "src" / "code_genereator" / "crews.py").exists():
            return parent
    return Path(__file__).resolve().parents[1]


def _cleanup_modules():
    for name in [
        "code_genereator.crews",
        "code_genereator",
        "code_genereator.tools",
        "code_genereator.tools.file_write_tool",
        "crewai",
        "crewai.project",
        "crewai.agents",
        "crewai.agents.agent_builder",
        "crewai.agents.agent_builder.base_agent",
        "dotenv",
    ]:
        if name in sys.modules:
            del sys.modules[name]


def _create_fake_dependencies():
    dotenv_module = types.ModuleType("dotenv")
    load_dotenv_mock = MagicMock()
    dotenv_module.load_dotenv = load_dotenv_mock
    sys.modules["dotenv"] = dotenv_module

    crewai_module = types.ModuleType("crewai")

    class FakeLLM:
        def __init__(self, model):
            self.model = model

    class FakeAgent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeTask:
        def __init__(self, config=None, **kwargs):
            self.config = config
            self.kwargs = kwargs

    class FakeCrew:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeProcess:
        sequential = "sequential"

    crewai_module.Agent = FakeAgent
    crewai_module.Crew = FakeCrew
    crewai_module.Process = FakeProcess
    crewai_module.Task = FakeTask
    crewai_module.LLM = FakeLLM
    sys.modules["crewai"] = crewai_module

    crewai_project = types.ModuleType("crewai.project")

    def CrewBase(cls):
        return cls

    def agent(func):
        return func

    def task(func):
        return func

    def crew(func):
        return func

    crewai_project.CrewBase = CrewBase
    crewai_project.agent = agent
    crewai_project.task = task
    crewai_project.crew = crew
    sys.modules["crewai.project"] = crewai_project

    base_agent_mod = types.ModuleType("crewai.agents.agent_builder.base_agent")

    class BaseAgent:
        pass

    base_agent_mod.BaseAgent = BaseAgent
    sys.modules["crewai.agents"] = types.ModuleType("crewai.agents")
    sys.modules["crewai.agents.agent_builder"] = types.ModuleType("crewai.agents.agent_builder")
    sys.modules["crewai.agents.agent_builder.base_agent"] = base_agent_mod

    code_gen_module = types.ModuleType("code_genereator")
    tools_module = types.ModuleType("code_genereator.tools")
    file_write_tool_module = types.ModuleType("code_genereator.tools.file_write_tool")

    class FileWriteTool:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    file_write_tool_module.FileWriteTool = FileWriteTool
    sys.modules["code_genereator"] = code_gen_module
    sys.modules["code_genereator.tools"] = tools_module
    sys.modules["code_genereator.tools.file_write_tool"] = file_write_tool_module

    return load_dotenv_mock


@pytest.fixture
def import_crews_module():
    def _import(os_getenv_value=None):
        _cleanup_modules()
        load_dotenv_mock = _create_fake_dependencies()

        def fake_getenv(key, default=None):
            return os_getenv_value if os_getenv_value is not None else default

        with patch("os.getenv", side_effect=fake_getenv) as getenv_mock, patch("builtins.print") as print_mock:
            repo_root = _find_repo_root()
            spec = importlib.util.spec_from_file_location(
                "code_genereator.crews", repo_root / "src" / "code_genereator" / "crews.py"
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules["code_genereator.crews"] = module
            spec.loader.exec_module(module)
        return module, load_dotenv_mock, print_mock, getenv_mock

    return _import


def test_module_model_default_and_load_dotenv_called(import_crews_module):
    """Validates MODEL default value and load_dotenv invocation when env var missing."""
    module, load_dotenv_mock, print_mock, getenv_mock = import_crews_module(os_getenv_value=None)
    assert module.MODEL == "gpt-4o"
    load_dotenv_mock.assert_called_once()
    getenv_mock.assert_called_with("MODEL", "gpt-4o")
    print_mock.assert_any_call(f"Using model: {module.MODEL}")


def test_module_model_from_env(import_crews_module):
    """Validates MODEL value from environment variable and prints correct message."""
    module, load_dotenv_mock, print_mock, getenv_mock = import_crews_module(os_getenv_value="custom-model")
    assert module.MODEL == "custom-model"
    load_dotenv_mock.assert_called_once()
    getenv_mock.assert_called_with("MODEL", "gpt-4o")
    print_mock.assert_any_call(f"Using model: {module.MODEL}")


def test_planning_architect_agent_creation(import_crews_module):
    """Ensures PlanningCrew.architect constructs Agent with expected configuration."""
    module, _, _, _ = import_crews_module()
    FakeAgent = sys.modules["crewai"].Agent
    FakeLLM = sys.modules["crewai"].LLM
    crew = module.PlanningCrew()
    crew.agents_config = {"architect": {"role": "arch"}}
    agent_obj = crew.architect()
    assert isinstance(agent_obj, FakeAgent)
    assert agent_obj.kwargs["config"] == {"role": "arch"}
    assert agent_obj.kwargs["verbose"] is True
    assert isinstance(agent_obj.kwargs["llm"], FakeLLM)
    assert agent_obj.kwargs["llm"].model == module.MODEL
    assert agent_obj.kwargs["reasoning"] is True
    assert agent_obj.kwargs["max_reasoning_attempts"] == 3


def test_planning_task_creation(import_crews_module):
    """Ensures PlanningCrew.planning_task constructs Task with proper configuration."""
    module, _, _, _ = import_crews_module()
    FakeTask = sys.modules["crewai"].Task
    crew = module.PlanningCrew()
    crew.tasks_config = {"planning_task": {"desc": "spec"}}
    task_obj = crew.planning_task()
    assert isinstance(task_obj, FakeTask)
    assert task_obj.config == {"desc": "spec"}


def test_planning_crew_creation(import_crews_module):
    """Ensures PlanningCrew.crew builds Crew with agents, tasks, and planning enabled."""
    module, _, _, _ = import_crews_module()
    FakeCrew = sys.modules["crewai"].Crew
    Process = sys.modules["crewai"].Process
    crew = module.PlanningCrew()
    crew.agents = [MagicMock(name="agent")]
    crew.tasks = [MagicMock(name="task")]
    crew_obj = crew.crew()
    assert isinstance(crew_obj, FakeCrew)
    assert crew_obj.kwargs["agents"] == crew.agents
    assert crew_obj.kwargs["tasks"] == crew.tasks
    assert crew_obj.kwargs["process"] == Process.sequential
    assert crew_obj.kwargs["verbose"] is True
    assert crew_obj.kwargs["planning"] is True


def test_planning_architect_missing_config_raises(import_crews_module):
    """Validates KeyError is raised when planning architect config is missing."""
    module, _, _, _ = import_crews_module()
    crew = module.PlanningCrew()
    crew.agents_config = {}
    with pytest.raises(KeyError):
        crew.architect()


def test_planning_task_missing_config_raises(import_crews_module):
    """Validates KeyError is raised when planning task config is missing."""
    module, _, _, _ = import_crews_module()
    crew = module.PlanningCrew()
    crew.tasks_config = {}
    with pytest.raises(KeyError):
        crew.planning_task()


@pytest.mark.parametrize("method_name", ["database_engineer", "backend_engineer", "frontend_engineer"])
def test_engineering_agent_methods(import_crews_module, method_name):
    """Ensures EngineeringCrew agent methods create Agent instances with proper config."""
    module, _, _, _ = import_crews_module()
    if not hasattr(module.EngineeringCrew, method_name):
        pytest.skip(f"{method_name} not present")
    FakeAgent = sys.modules["crewai"].Agent
    FakeLLM = sys.modules["crewai"].LLM
    crew = module.EngineeringCrew()
    crew.agents_config = {method_name: {"name": method_name}}
    agent_obj = getattr(crew, method_name)()
    assert isinstance(agent_obj, FakeAgent)
    assert agent_obj.kwargs["config"] == {"name": method_name}
    if "llm" in agent_obj.kwargs:
        assert isinstance(agent_obj.kwargs["llm"], FakeLLM)
        assert agent_obj.kwargs["llm"].model == module.MODEL


@pytest.mark.parametrize("method_name", ["database_task", "backend_task", "frontend_task"])
def test_engineering_task_methods(import_crews_module, method_name):
    """Ensures EngineeringCrew task methods create Task instances with proper config."""
    module, _, _, _ = import_crews_module()
    if not hasattr(module.EngineeringCrew, method_name):
        pytest.skip(f"{method_name} not present")
    FakeTask = sys.modules["crewai"].Task
    crew = module.EngineeringCrew()
    crew.tasks_config = {method_name: {"task": method_name}}
    task_obj = getattr(crew, method_name)()
    assert isinstance(task_obj, FakeTask)
    assert task_obj.config == {"task": method_name}


def test_engineering_crew_creation(import_crews_module):
    """Ensures EngineeringCrew.crew builds Crew with agents and tasks."""
    module, _, _, _ = import_crews_module()
    if not hasattr(module.EngineeringCrew, "crew"):
        pytest.skip("EngineeringCrew.crew not present")
    FakeCrew = sys.modules["crewai"].Crew
    Process = sys.modules["crewai"].Process
    crew = module.EngineeringCrew()
    crew.agents = [MagicMock(name="agent")]
    crew.tasks = [MagicMock(name="task")]
    crew_obj = crew.crew()
    assert isinstance(crew_obj, FakeCrew)
    assert crew_obj.kwargs["agents"] == crew.agents
    assert crew_obj.kwargs["tasks"] == crew.tasks
    if "process" in crew_obj.kwargs:
        assert crew_obj.kwargs["process"] == Process.sequential


def test_engineering_agent_missing_config_raises(import_crews_module):
    """Validates KeyError when engineering agent configuration is missing."""
    module, _, _, _ = import_crews_module()
    if not hasattr(module.EngineeringCrew, "database_engineer"):
        pytest.skip("database_engineer not present")
    crew = module.EngineeringCrew()
    crew.agents_config = {}
    with pytest.raises(KeyError):
        crew.database_engineer()


def test_engineering_task_missing_config_raises(import_crews_module):
    """Validates KeyError when engineering task configuration is missing."""
    module, _, _, _ = import_crews_module()
    if not hasattr(module.EngineeringCrew, "database_task"):
        pytest.skip("database_task not present")
    crew = module.EngineeringCrew()
    crew.tasks_config = {}
    with pytest.raises(KeyError):
        crew.database_task()


def test_judgecrew_methods_and_crew(import_crews_module):
    """Dynamically exercises JudgeCrew agent/task methods and crew creation."""
    module, _, _, _ = import_crews_module()
    if not hasattr(module, "JudgeCrew"):
        pytest.skip("JudgeCrew not present")
    FakeAgent = sys.modules["crewai"].Agent
    FakeTask = sys.modules["crewai"].Task
    FakeCrew = sys.modules["crewai"].Crew
    Process = sys.modules["crewai"].Process

    judge = module.JudgeCrew()
    method_names = [
        name for name, attr in module.JudgeCrew.__dict__.items()
        if callable(attr) and not name.startswith("_") and name != "crew"
    ]
    agent_methods = [name for name in method_names if "task" not in name]
    task_methods = [name for name in method_names if "task" in name]

    judge.agents_config = {name: {"name": name} for name in agent_methods}
    judge.tasks_config = {name: {"name": name} for name in task_methods}

    for name in agent_methods:
        agent_obj = getattr(judge, name)()
        assert isinstance(agent_obj, FakeAgent)
        assert agent_obj.kwargs["config"] == {"name": name}

    for name in task_methods:
        task_obj = getattr(judge, name)()
        assert isinstance(task_obj, FakeTask)
        assert task_obj.config == {"name": name}

    judge.agents = [MagicMock(name="agent")]
    judge.tasks = [MagicMock(name="task")]
    crew_obj = judge.crew()
    assert isinstance(crew_obj, FakeCrew)
    assert crew_obj.kwargs["agents"] == judge.agents
    assert crew_obj.kwargs["tasks"] == judge.tasks
    if "process" in crew_obj.kwargs:
        assert crew_obj.kwargs["process"] == Process.sequential