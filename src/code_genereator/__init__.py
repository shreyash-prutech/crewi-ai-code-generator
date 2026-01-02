"""
Agentic Software Factory

A CrewAI Flow-based system for generating complete software projects
from natural language requirements.

The system uses three specialized crews:
- PlanningCrew: Generates technical specifications
- EngineeringCrew: Implements database, backend, and frontend code
- JudgeCrew: Validates integration and produces final reports
"""

from code_genereator.state import DevelopmentState
from code_genereator.crews import PlanningCrew, EngineeringCrew, JudgeCrew
from code_genereator.main import SoftwareDevFlow, run, main, kickoff, plot

__all__ = [
    "DevelopmentState",
    "PlanningCrew",
    "EngineeringCrew",
    "JudgeCrew",
    "SoftwareDevFlow",
    "run",
    "main",
    "kickoff",
    "plot",
]

__version__ = "1.0.0"
