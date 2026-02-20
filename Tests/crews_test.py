import os
import pytest
from unittest.mock import MagicMock

class MockLLM:
    def __init__(self, model):
        self.model = model

class MockAgent:
    def __init__(self, config, verbose=False, llm=None, reasoning=False, max_reasoning_attempts=None):
        self.config = config
        self.verbose = verbose
        self.llm = llm
        self.reasoning = reasoning
        self.max_reasoning_attempts = max_reasoning_attempts

class MockTask:
    def __init__(self, config):
        self.config = config

class MockCrew:
    def __init__(self, agents, tasks, process, verbose=False, planning=False):
        self.agents = agents
        self.tasks = tasks
        self.process = process
        self.verbose = verbose
        self.planning = planning

class MockProcess:
    sequential = "sequential"

class PlanningCrew:
    agents_config = {"architect": {"role": "architect"}}
    tasks_config = {"planning_task": {"name": "plan"}}

    def __init__(self, model=None):
        self.model = model or os.getenv("MODEL", "gpt-4o")
        self.agents = []
        self.tasks = []

    def architect(self):
        return MockAgent(
            config=self.agents_config["architect"],
            verbose=True,
            llm=MockLLM(model=self.model),
            reasoning=True,
            max_reasoning_attempts=3,
        )

    def planning_task(self):
        return MockTask(config=self.tasks_config["planning_task"])

    def crew(self):
        return MockCrew(
            agents=self.agents,
            tasks=self.tasks,
            process=MockProcess.sequential,
            verbose=True,
            planning=True,
        )

@pytest.fixture
def crew_with_defaults(monkeypatch):
    """Provide a PlanningCrew instance with default environment."""
    monkeypatch.delenv("MODEL", raising=False)
    return PlanningCrew()

def test_planning_crew_architect_agent_configuration(crew_with_defaults):
    """Validate architect agent is created with expected config and model."""
    agent = crew_with_defaults.architect()
    assert agent.config == {"role": "architect"}
    assert agent.verbose is True
    assert agent.reasoning is True
    assert agent.max_reasoning_attempts == 3
    assert isinstance(agent.llm, MockLLM)
    assert agent.llm.model == "gpt-4o"

@pytest.mark.parametrize("model_value", ["gpt-3.5", "custom-model"])
def test_planning_crew_respects_model_env(monkeypatch, model_value):
    """Ensure model is pulled from environment when set."""
    monkeypatch.setenv("MODEL", model_value)
    crew = PlanningCrew()
    agent = crew.architect()
    assert agent.llm.model == model_value

def test_planning_task_missing_config_raises_keyerror():
    """Validate missing task configuration raises KeyError."""
    crew = PlanningCrew()
    crew.tasks_config = {}
    with pytest.raises(KeyError):
        crew.planning_task()

def test_crew_creation_uses_sequential_process_and_flags():
    """Validate crew creation uses sequential process and sets flags."""
    crew = PlanningCrew()
    crew.agents = [MagicMock()]
    crew.tasks = [MagicMock()]
    created = crew.crew()
    assert created.process == MockProcess.sequential
    assert created.verbose is True
    assert created.planning is True
    assert created.agents == crew.agents
    assert created.tasks == crew.tasks