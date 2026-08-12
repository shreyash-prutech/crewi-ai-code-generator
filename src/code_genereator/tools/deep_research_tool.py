"""DeepResearchTool for structured research planning.

This tool transforms a requirement and optional context into a deterministic
Markdown research plan for the agentic software factory.
"""

from typing import Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepResearchToolInput(BaseModel):
    requirement: str = Field(
        ...,
        description="The user requirement or problem statement to research"
    )
    context: Optional[str] = Field(
        default="",
        description="Optional gathered context, notes, memories, or prior findings"
    )


class DeepResearchTool(BaseTool):
    name: str = "deep_research_tool"
    description: str = (
        "Produces a structured Markdown research plan from a requirement and "
        "optional context. Use this to gather, analyze, and synthesize notes "
        "before code generation."
    )
    args_schema: Type[BaseModel] = DeepResearchToolInput

    def _run(self, requirement: str, context: str = "") -> str:
        requirement_text = (requirement or "").strip()
        context_text = (context or "").strip()

        context_summary = (
            context_text
            if context_text
            else "No additional context or memory was provided."
        )

        known_items = []
        unknown_items = []
        if requirement_text:
            known_items.append(f"Primary requirement: {requirement_text}")
        else:
            unknown_items.append("The requirement text is empty or missing.")

        if context_text:
            known_items.append("Supplementary notes and memories were provided.")
        else:
            unknown_items.append("No supplementary notes, memories, or prior findings were provided.")

        assumptions = [
            "The implementation should be aligned with the existing CrewAI workflow.",
            "The output should be deterministic and suitable for saving as Markdown.",
        ]
        if not context_text:
            assumptions.append("Any missing details will need to be inferred conservatively from the requirement alone.")

        technical_approach = [
            "Parse and normalize the requirement and any supplied context.",
            "Group findings into context, analysis, gaps, assumptions, synthesis, and roadmap sections.",
            "Translate the research output into a Markdown plan that can guide later code generation.",
        ]

        design_decisions = [
            "Use a single tool with a Pydantic input schema for predictable agent integration.",
            "Keep the research output local and deterministic without external dependencies.",
            "Return Markdown directly so the result can be stored or reviewed without transformation.",
        ]

        trade_offs = [
            "Deterministic synthesis improves repeatability but cannot discover new external facts.",
            "A compact structured summary is easier to consume but may omit deeper exploratory nuance.",
            "Using the provided context keeps the workflow grounded but depends on the quality of prior notes.",
        ]

        risks = [
            "Incomplete requirements may lead to assumptions that diverge from the user's intent.",
            "Overly broad context may dilute the final research focus.",
            "Downstream code generation may inherit ambiguities that were not resolved in the research stage.",
        ]

        roadmap = [
            "1. Confirm the requirement and capture all available notes or memories.",
            "2. Extract known facts, constraints, and desired outcomes.",
            "3. Identify gaps, ambiguities, and necessary assumptions.",
            "4. Convert the findings into a technical approach and design decisions.",
            "5. Review trade-offs and risks to refine implementation boundaries.",
            "6. Produce the final Markdown research plan for the engineering workflow.",
        ]

        lines = [
            "# Deep Research Plan",
            "",
            "## Problem analysis",
            f"- Requirement: {requirement_text or 'Not provided'}",
            f"- Context gathered: {context_summary}",
            "- Known information:",
        ]
        lines.extend([f"  - {item}" for item in known_items] or ["  - None identified."])
        lines.append("- Gaps and assumptions:")
        if unknown_items:
            lines.extend([f"  - {item}" for item in unknown_items])
        else:
            lines.append("  - No critical gaps identified from the provided input.")
        lines.extend([f"  - Assumption: {item}" for item in assumptions])

        lines.extend([
            "",
            "## Technical approach",
        ])
        lines.extend([f"- {item}" for item in technical_approach])

        lines.extend([
            "",
            "## Design decisions",
        ])
        lines.extend([f"- {item}" for item in design_decisions])

        lines.extend([
            "",
            "## Trade-offs",
        ])
        lines.extend([f"- {item}" for item in trade_offs])

        lines.extend([
            "",
            "## Risks",
        ])
        lines.extend([f"- {item}" for item in risks])

        lines.extend([
            "",
            "## Detailed implementation roadmap",
        ])
        lines.extend([f"- {item}" for item in roadmap])

        return "\n".join(lines)
