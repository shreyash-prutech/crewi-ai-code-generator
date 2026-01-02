"""
Specialized Crews for the Agentic Software Factory.

This module defines three specialized crews:
- PlanningCrew: Generates technical specifications
- EngineeringCrew: Implements database, backend, and frontend code
- JudgeCrew: Validates and integrates all components
"""

import os
from dotenv import load_dotenv

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from code_genereator.tools.file_write_tool import FileWriteTool

# Load environment variables from .env file
load_dotenv()

# Get the model from environment variable, default to gpt-4o if not set
MODEL = os.getenv("MODEL", "gpt-4o")
print(f"Using model: {MODEL}")


# PLANNING CREW

@CrewBase
class PlanningCrew:
    """
    Planning Crew responsible for generating technical specifications.

    Contains the Architect agent who analyzes requirements and produces
    a detailed JSON-like technical spec for the engineering team.
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/planning_agents.yaml"
    tasks_config = "config/planning_tasks.yaml"

    @agent
    def architect(self) -> Agent:
        """
        The Architect agent - designs system architecture and technical specs.
        Uses planning and reasoning capabilities for thorough analysis.
        """
        return Agent(
            config=self.agents_config["architect"],  # type: ignore[index]
            verbose=True,
            llm=LLM(model=MODEL),
            reasoning=True,
            max_reasoning_attempts=3,
        )

    @task
    def planning_task(self) -> Task:
        """
        Task to generate a detailed technical specification.
        """
        return Task(
            config=self.tasks_config["planning_task"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Planning Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=True,
        )



# ENGINEERING CREW

@CrewBase
class EngineeringCrew:
    """
    Engineering Crew responsible for implementing the actual code.

    Contains three specialized agents:
    - Database Agent: Generates SQL schemas and ORM models
    - Backend Agent: Generates API endpoints and business logic
    - Frontend Agent: Generates UI components and frontend code

    Uses sequential process to ensure each tier builds on the previous.
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/engineering_agents.yaml"
    tasks_config = "config/engineering_tasks.yaml"

    @agent
    def database_engineer(self) -> Agent:
        """
        Database Engineer - designs and implements database schemas.
        """
        return Agent(
            config=self.agents_config["database_engineer"],  # type: ignore[index]
            verbose=True,
            llm=LLM(model=MODEL),
            reasoning=True,
            max_reasoning_attempts=3,
        )

    @agent
    def backend_engineer(self) -> Agent:
        """
        Backend Engineer - implements APIs and business logic.
        Receives context from the Database Engineer.
        """
        return Agent(
            config=self.agents_config["backend_engineer"],  # type: ignore[index]
            verbose=True,
            llm=LLM(model=MODEL),
            reasoning=True,
            max_reasoning_attempts=3,
        )

    @agent
    def frontend_engineer(self) -> Agent:
        """
        Frontend Engineer - implements UI components and frontend logic.
        Receives context from the Backend Engineer.
        """
        return Agent(
            config=self.agents_config["frontend_engineer"],  # type: ignore[index]
            verbose=True,
            llm=LLM(model=MODEL),
            reasoning=True,
            max_reasoning_attempts=3,
        )

    @task
    def database_task(self) -> Task:
        """
        Task to generate database schemas and models.
        """
        return Task(
            config=self.tasks_config["database_task"],  # type: ignore[index]
        )

    @task
    def backend_task(self) -> Task:
        """
        Task to generate backend APIs.
        Depends on database_task output.
        """
        return Task(
            config=self.tasks_config["backend_task"],  # type: ignore[index]
            context=[self.database_task()],
        )

    @task
    def frontend_task(self) -> Task:
        """
        Task to generate frontend UI.
        Depends on backend_task output.
        """
        return Task(
            config=self.tasks_config["frontend_task"],  # type: ignore[index]
            context=[self.backend_task()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Engineering Crew with sequential process"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=True,
        )



# JUDGE CREW

@CrewBase
class JudgeCrew:
    """
    Judge Crew responsible for final validation and integration.

    Contains the Judge agent who validates integration across all tiers,
    checks naming consistency, and produces a final Markdown report.
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/judge_agents.yaml"
    tasks_config = "config/judge_tasks.yaml"

    @agent
    def judge(self) -> Agent:
        """
        The Judge agent - validates and integrates all code components.
        Uses reasoning capabilities for thorough validation.
        Has access to FileWriteTool to save final output.
        """
        return Agent(
            config=self.agents_config["judge"],  # type: ignore[index]
            verbose=True,
            llm=LLM(model=MODEL),
            tools=[FileWriteTool()],
            reasoning=True,
            max_reasoning_attempts=3,
        )

    @task
    def validation_task(self) -> Task:
        """
        Task to validate integration and produce final report.
        """
        return Task(
            config=self.tasks_config["validation_task"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Judge Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=True,
        )
