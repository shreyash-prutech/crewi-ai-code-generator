import os
from datetime import datetime
from typing import Type

from code_genereator.tools.file_write_tool import (FileWriteTool,
                                                   FileWriteToolInput)
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepResearchToolInput(BaseModel):
    requirement: str = Field(..., description="The software requirement or feature request to analyze")
    context: str = Field(..., description="Relevant context and memories for the research process")

class DeepResearchTool(BaseTool):
    name: str = "deep_research_tool"
    description: str = (
        "Performs deep research and generates a Markdown research plan. "
        "The plan includes problem analysis, technical approach, design decisions, trade-offs, risks, and a detailed implementation roadmap."
    )
    args_schema: Type[BaseModel] = DeepResearchToolInput

    def _run(self, requirement: str, context: str) -> str:
        # Perform deep research
        problem_analysis = self.analyze_problem(requirement, context)
        technical_approach = self.define_technical_approach(requirement, context)
        design_decisions = self.make_design_decisions(requirement, context)
        trade_offs = self.identify_trade_offs(requirement, context)
        risks = self.assess_risks(requirement, context)
        implementation_roadmap = self.create_implementation_roadmap(requirement, context)

        # Generate Markdown content
        markdown_content = self.generate_markdown(
            problem_analysis, technical_approach, design_decisions, trade_offs, risks, implementation_roadmap
        )

        # Save the Markdown file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"dist/research_plan_{timestamp}.md"
        file_write_tool = FileWriteTool()
        file_write_tool._run(file_path, markdown_content)

        return file_path

    def analyze_problem(self, requirement: str, context: str) -> str:
        # Analyze the problem based on the requirement and context
        return f"Problem analysis for requirement: {requirement}\nContext: {context}"

    def define_technical_approach(self, requirement: str, context: str) -> str:
        # Define the technical approach based on the requirement and context
        return f"Technical approach for requirement: {requirement}\nContext: {context}"

    def make_design_decisions(self, requirement: str, context: str) -> str:
        # Make design decisions based on the requirement and context
        return f"Design decisions for requirement: {requirement}\nContext: {context}"

    def identify_trade_offs(self, requirement: str, context: str) -> str:
        # Identify trade-offs based on the requirement and context
        return f"Trade-offs for requirement: {requirement}\nContext: {context}"

    def assess_risks(self, requirement: str, context: str) -> str:
        # Assess risks based on the requirement and context
        return f"Risks for requirement: {requirement}\nContext: {context}"

    def create_implementation_roadmap(self, requirement: str, context: str) -> str:
        # Create an implementation roadmap based on the requirement and context
        return f"Implementation roadmap for requirement: {requirement}\nContext: {context}"

    def generate_markdown(self, problem_analysis: str, technical_approach: str, design_decisions: str, trade_offs: str, risks: str, implementation_roadmap: str) -> str:
        # Generate the Markdown content for the research plan
        return f"""# Research Plan

## Problem Analysis
{problem_analysis}

## Technical Approach
{technical_approach}

## Design Decisions
{design_decisions}

## Trade-offs
{trade_offs}

## Risks
{risks}

## Implementation Roadmap
{implementation_roadmap}
"""
