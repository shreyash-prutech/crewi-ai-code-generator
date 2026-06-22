"""
Research tools for the Agentic Software Factory.

This module provides a focused research tool for planning agents that need
additional implementation context while generating technical specifications.
"""

from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ResearchToolInput(BaseModel):
    """
    Input schema for ResearchTool.
    """

    query: str = Field(..., description="Research query to investigate.")


class ResearchTool(BaseTool):
    """
    Tool used by planning agents to perform focused technical research.
    """

    name: str = "Research Tool"
    description: str = (
        "Provides focused research guidance for architecture and planning decisions. "
        "Use this tool to investigate technologies, APIs, implementation constraints, "
        "and best practices needed for a technical specification."
    )
    args_schema: Type[BaseModel] = ResearchToolInput

    def _run(self, query: str) -> str:
        """
        Run focused research for the supplied query.
        """
        return (
            "Research request received for: "
            f"{query}\n\n"
            "Review authoritative documentation, compatibility constraints, security "
            "requirements, integration boundaries, and implementation best practices "
            "before finalizing the technical specification."
        )
