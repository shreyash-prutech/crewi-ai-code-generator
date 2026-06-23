import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import importlib.util

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

spec = importlib.util.spec_from_file_location("crews", REPO_ROOT / "src/code_genereator/crews.py")
crews_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crews_module)

PlanningCrew = crews_module.PlanningCrew
EngineeringCrew = crews_module.EngineeringCrew
JudgeCrew = crews_module.JudgeCrew

@pytest.fixture
def mock_agent():
    """Mock Agent instance for testing"""
    mock = MagicMock()
    mock.config = {"role": "test_role", "goal": "test_goal"}
    return mock

@pytest.fixture
def mock_task():
    """Mock Task instance for testing"""
    mock = MagicMock()
    mock.config = {"description": "test_description"}
    return mock

@pytest.fixture
def mock_crew():
    """Mock Crew instance for testing"""
    mock = MagicMock()
    return mock

@patch('crews_module.load_dotenv')
@patch('crews_module.os.getenv')
def test_model_environment_variable_loading(mock_getenv, mock_load_dotenv):
    """Test that MODEL environment variable is loaded correctly"""
    mock_getenv.return_value = "gpt-3.5-turbo"
    
    # Re-import to trigger environment loading
    importlib.reload(crews_module)
    
    mock_load_dotenv.assert_called_once()
    mock_getenv.assert_called_with("MODEL", "gpt-4o")

@patch('crews_module.Agent')
@patch('crews_module.LLM')
def test_planning_crew_architect_agent_creation(mock_llm, mock_agent):
    """Test that PlanningCrew creates architect agent with correct configuration"""
    mock_agent_instance = MagicMock()
    mock_agent.return_value = mock_agent_instance
    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance
    
    planning_crew = PlanningCrew()
    planning_crew.agents_config = {"architect": {"role": "architect", "goal": "design"}}
    
    result = planning_crew.architect()
    
    mock_llm.assert_called_once_with(model=crews_module.MODEL)
    mock_agent.assert_called_once_with(
        config={"role": "architect", "goal": "design"},
        verbose=True,
        llm=mock_llm_instance,
        reasoning=True,
        max_reasoning_attempts=3
    )
    assert result == mock_agent_instance

@patch('crews_module.Task')
def test_planning_crew_planning_task_creation(mock_task):
    """Test that PlanningCrew creates planning task with correct configuration"""
    mock_task_instance = MagicMock()
    mock_task.return_value = mock_task_instance
    
    planning_crew = PlanningCrew()
    planning_crew.tasks_config = {"planning_task": {"description": "plan system"}}
    
    result = planning_crew.planning_task()
    
    mock_task.assert_called_once_with(
        config={"description": "plan system"}
    )
    assert result == mock_task_instance

@patch('crews_module.Crew')
@patch('crews_module.Process')
def test_planning_crew_crew_creation(mock_process, mock_crew):
    """Test that PlanningCrew creates crew with correct configuration"""
    mock_crew_instance = MagicMock()
    mock_crew.return_value = mock_crew_instance
    mock_process.sequential = "sequential"
    
    planning_crew = PlanningCrew()
    planning_crew.agents = [MagicMock(), MagicMock()]
    planning_crew.tasks = [MagicMock()]
    
    result = planning_crew.crew()
    
    mock_crew.assert_called_once_with(
        agents=planning_crew.agents,
        tasks=planning_crew.tasks,
        process="sequential",
        verbose=True,
        planning=True
    )
    assert result == mock_crew_instance

@patch('crews_module.Agent')
@patch('crews_module.LLM')
def test_engineering_crew_database_engineer_creation(mock_llm, mock_agent):
    """Test that EngineeringCrew creates database engineer agent"""
    mock_agent_instance = MagicMock()
    mock_agent.return_value = mock_agent_instance
    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance
    
    engineering_crew = EngineeringCrew()
    engineering_crew.agents_config = {"database_engineer": {"role": "db_engineer"}}
    
    result = engineering_crew.database_engineer()
    
    mock_llm.assert_called_once_with(model=crews_module.MODEL)
    mock_agent.assert_called_once_with(
        config={"role": "db_engineer"},
        verbose=True,
        llm=mock_llm_instance,
        tools=[crews_module.FileWriteTool()]
    )
    assert result == mock_agent_instance

@patch('crews_module.Agent')
@patch('crews_module.LLM')
def test_engineering_crew_backend_engineer_creation(mock_llm, mock_agent):
    """Test that EngineeringCrew creates backend engineer agent"""
    mock_agent_instance = MagicMock()
    mock_agent.return_value = mock_agent_instance
    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance
    
    engineering_crew = EngineeringCrew()
    engineering_crew.agents_config = {"backend_engineer": {"role": "backend_engineer"}}
    
    result = engineering_crew.backend_engineer()
    
    mock_llm.assert_called_once_with(model=crews_module.MODEL)
    mock_agent.assert_called_once_with(
        config={"role": "backend_engineer"},
        verbose=True,
        llm=mock_llm_instance,
        tools=[crews_module.FileWriteTool()]
    )
    assert result == mock_agent_instance

@patch('crews_module.Agent')
@patch('crews_module.LLM')
def test_engineering_crew_frontend_engineer_creation(mock_llm, mock_agent):
    """Test that EngineeringCrew creates frontend engineer agent"""
    mock_agent_instance = MagicMock()
    mock_agent.return_value = mock_agent_instance
    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance
    
    engineering_crew = EngineeringCrew()
    engineering_crew.agents_config = {"frontend_engineer": {"role": "frontend_engineer"}}
    
    result = engineering_crew.frontend_engineer()
    
    mock_llm.assert_called_once_with(model=crews_module.MODEL)
    mock_agent.assert_called_once_with(
        config={"role": "frontend_engineer"},
        verbose=True,
        llm=mock_llm_instance,
        tools=[crews_module.FileWriteTool()]
    )
    assert result == mock_agent_instance

@patch('crews_module.Task')
def test_engineering_crew_database_task_creation(mock_task):
    """Test that EngineeringCrew creates database task"""
    mock_task_instance = MagicMock()
    mock_task.return_value = mock_task_instance
    
    engineering_crew = EngineeringCrew()
    engineering_crew.tasks_config = {"database_task": {"description": "create database"}}
    
    result = engineering_crew.database_task()
    
    mock_task.assert_called_once_with(
        config={"description": "create database"}
    )
    assert result == mock_task_instance

@patch('crews_module.Task')
def test_engineering_crew_backend_task_creation(mock_task):
    """Test that EngineeringCrew creates backend task"""
    mock_task_instance = MagicMock()
    mock_task.return_value = mock_task_instance
    
    engineering_crew = EngineeringCrew()
    engineering_crew.tasks_config = {"backend_task": {"description": "create backend"}}
    
    result = engineering_crew.backend_task()
    
    mock_task.assert_called_once_with(
        config={"description": "create backend"}
    )
    assert result == mock_task_instance

@patch('crews_module.Task')
def test_engineering_crew_frontend_task_creation(mock_task):
    """Test that EngineeringCrew creates frontend task"""
    mock_task_instance = MagicMock()
    mock_task.return_value = mock_task_instance
    
    engineering_crew = EngineeringCrew()
    engineering_crew.tasks_config = {"frontend_task": {"description": "create frontend"}}
    
    result = engineering_crew.frontend_task()
    
    mock_task.assert_called_once_with(
        config={"description": "create frontend"}
    )
    assert result == mock_task_instance

@patch('crews_module.Crew')
@patch('crews_module.Process')
def test_engineering_crew_crew_creation(mock_process, mock_crew):
    """Test that EngineeringCrew creates crew with sequential process"""
    mock_crew_instance = MagicMock()
    mock_crew.return_value = mock_crew_instance
    mock_process.sequential = "sequential"
    
    engineering_crew = EngineeringCrew()
    engineering_crew.agents = [MagicMock(), MagicMock(), MagicMock()]
    engineering_crew.tasks = [MagicMock(), MagicMock(), MagicMock()]
    
    result = engineering_crew.crew()
    
    mock_crew.assert_called_once_with(
        agents=engineering_crew.agents,
        tasks=engineering_crew.tasks,
        process="sequential",
        verbose=True
    )
    assert result == mock_crew_instance

@patch('crews_module.Agent')
@patch('crews_module.LLM')
def test_judge_crew_judge_agent_creation(mock_llm, mock_agent):
    """Test that JudgeCrew creates judge agent"""
    mock_agent_instance = MagicMock()
    mock_agent.return_value = mock_agent_instance
    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance
    
    judge_crew = JudgeCrew()
    judge_crew.agents_config = {"judge": {"role": "judge", "goal": "validate"}}
    
    result = judge_crew.judge()
    
    mock_llm.assert_called_once_with(model=crews_module.MODEL)
    mock_agent.assert_called_once_with(
        config={"role": "judge", "goal": "validate"},
        verbose=True,
        llm=mock_llm_instance,
        reasoning=True,
        max_reasoning_attempts=5
    )
    assert result == mock_agent_instance

@patch('crews_module.Task')
def test_judge_crew_validation_task_creation(mock_task):
    """Test that JudgeCrew creates validation task"""
    mock_task_instance = MagicMock()
    mock_task.return_value = mock_task_instance
    
    judge_crew = JudgeCrew()
    judge_crew.tasks_config = {"validation_task": {"description": "validate code"}}
    
    result = judge_crew.validation_task()
    
    mock_task.assert_called_once_with(
        config={"description": "validate code"}
    )
    assert result == mock_task_instance

@patch('crews_module.Crew')
@patch('crews_module.Process')
def test_judge_crew_crew_creation(mock_process, mock_crew):
    """Test that JudgeCrew creates crew with sequential process and planning"""
    mock_crew_instance = MagicMock()
    mock_crew.return_value = mock_crew_instance
    mock_process.sequential = "sequential"
    
    judge_crew = JudgeCrew()
    judge_crew.agents = [MagicMock()]
    judge_crew.tasks = [MagicMock()]
    
    result = judge_crew.crew()
    
    mock_crew.assert_called_once_with(
        agents=judge_crew.agents,
        tasks=judge_crew.tasks,
        process="sequential",
        verbose=True,
        planning=True
    )
    assert result == mock_crew_instance

def test_planning_crew_instantiation():
    """Test that PlanningCrew can be instantiated"""
    crew = PlanningCrew()
    assert crew is not None
    assert hasattr(crew, 'agents_config')
    assert hasattr(crew, 'tasks_config')
    assert crew.agents_config == "config/planning_agents.yaml"
    assert crew.tasks_config == "config/planning_tasks.yaml"

def test_engineering_crew_instantiation():
    """Test that EngineeringCrew can be instantiated"""
    crew = EngineeringCrew()
    assert crew is not None
    assert hasattr(crew, 'agents_config')
    assert hasattr(crew, 'tasks_config')
    assert crew.agents_config == "config/engineering_agents.yaml"
    assert crew.tasks_config == "config/engineering_tasks.yaml"

def test_judge_crew_instantiation():
    """Test that JudgeCrew can be instantiated"""
    crew = JudgeCrew()
    assert crew is not None
    assert hasattr(crew, 'agents_config')
    assert hasattr(crew, 'tasks_config')
    assert crew.agents_config == "config/judge_agents.yaml"
    assert crew.tasks_config == "config/judge_tasks.yaml"

@patch('crews_module.FileWriteTool')
def test_file_write_tool_usage_in_engineering_agents(mock_file_write_tool):
    """Test that engineering agents use FileWriteTool"""
    mock_tool_instance = MagicMock()
    mock_file_write_tool.return_value = mock_tool_instance
    
    with patch('crews_module.Agent') as mock_agent, \
         patch('crews_module.LLM') as mock_llm:
        
        engineering_crew = EngineeringCrew()
        engineering_crew.agents_config = {"database_engineer": {"role": "db"}}
        
        engineering_crew.database_engineer()
        
        mock_file_write_tool.assert_called_once()
        mock_agent.assert_called_once()
        call_args = mock_agent.call_args
        assert 'tools' in call_args.kwargs
        assert call_args.kwargs['tools'] == [mock_tool_instance]

def test_model_default_value():
    """Test that MODEL defaults to gpt-4o when environment variable is not set"""
    with patch('crews_module.os.getenv') as mock_getenv:
        mock_getenv.return_value = None
        importlib.reload(crews_module)
        mock_getenv.assert_called_with("MODEL", "gpt-4o")

@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo", "gpt-4", "claude-3", "llama-2"])
def test_model_configuration_with_different_models(model_name):
    """Test that different model names are handled correctly"""
    with patch('crews_module.os.getenv') as mock_getenv:
        mock_getenv.return_value