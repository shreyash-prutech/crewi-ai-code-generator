import re
from typing import List, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepResearchToolInput(BaseModel):
    topic: str = Field(..., description="The research topic or feature area to investigate.")
    plan_context: str = Field(..., description="The current plan, specification, or design context to analyze.")
    memory_context: Optional[str] = Field(
        default=None,
        description="Optional workflow memory, prior notes, or historical context to incorporate."
    )
    additional_context: Optional[str] = Field(
        default=None,
        description="Optional extra context, assumptions, constraints, or implementation notes."
    )


class DeepResearchTool(BaseTool):
    name: str = "deep_research_tool"
    description: str = (
        "Performs structured deep research over a topic using plan/spec context and optional memory/context inputs, "
        "then returns a clean Markdown research plan with analysis, decisions, risks, gaps, and roadmap."
    )
    args_schema: Type[BaseModel] = DeepResearchToolInput

    def _normalize_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [line.rstrip() for line in normalized.split("\n")]
        collapsed_lines: List[str] = []
        previous_blank = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if not previous_blank:
                    collapsed_lines.append("")
                previous_blank = True
                continue
            collapsed_lines.append(stripped)
            previous_blank = False
        return "\n".join(collapsed_lines).strip()

    def _split_blocks(self, text: str) -> List[str]:
        if not text:
            return []
        blocks = re.split(r"\n\s*\n", text.strip())
        results: List[str] = []
        for block in blocks:
            cleaned = block.strip()
            if cleaned:
                results.append(cleaned)
        return results

    def _extract_key_points(self, text: str, limit: int = 8) -> List[str]:
        if not text:
            return []
        points: List[str] = []
        seen = set()
        for raw_line in text.split("\n"):
            line = raw_line.strip()
            if not line:
                continue
            line = re.sub(r"^[\-\*\u2022]\s*", "", line)
            line = re.sub(r"^\d+[.)]\s*", "", line)
            if len(line) < 4:
                continue
            lowered = line.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            points.append(line)
            if len(points) >= limit:
                break
        return points

    def _derive_problem_analysis(self, topic: str, plan_context: str, memory_blocks: List[str], additional_blocks: List[str]) -> List[str]:
        points = self._extract_key_points(plan_context, limit=4)
        memory_points = self._extract_key_points("\n".join(memory_blocks), limit=3)
        extra_points = self._extract_key_points("\n".join(additional_blocks), limit=3)
        analysis: List[str] = []
        analysis.append(f"The work centers on {topic}, with the current plan/spec defining the primary objective and implementation boundaries.")
        if points:
            analysis.append(f"The plan indicates key requirements such as {points[0].rstrip('.')}.")
        if len(points) > 1:
            analysis.append(f"Additional specification detail suggests attention to {points[1].rstrip('.')}.")
        if memory_points:
            analysis.append(f"Prior workflow context highlights {memory_points[0].rstrip('.')}, which should influence the research direction.")
        if extra_points:
            analysis.append(f"Supplemental notes reinforce {extra_points[0].rstrip('.')}.")
        analysis.append("The main problem is to translate the specification into a reliable implementation strategy while preserving compatibility with the existing workflow.")
        analysis.append("Known unknowns should be surfaced early so the downstream code-generation step can proceed with fewer assumptions.")
        return analysis

    def _derive_technical_approach(self, topic: str, plan_context: str, memory_blocks: List[str], additional_blocks: List[str]) -> List[str]:
        key_points = self._extract_key_points(plan_context, limit=5)
        approach: List[str] = []
        approach.append(f"Use the provided plan for {topic} as the source of truth, then decompose it into implementation concerns, interfaces, and validation steps.")
        approach.append("Start by mapping the specification into entities, responsibilities, and dependencies, then identify the smallest coherent execution slices.")
        if key_points:
            approach.append(f"Important technical anchors include {key_points[0].rstrip('.')}, which should be implemented first.")
        if len(key_points) > 1:
            approach.append(f"Follow with {key_points[1].rstrip('.')}, ensuring downstream components consume stable contracts.")
        if memory_blocks:
            approach.append("Incorporate memory/context by reconciling historical decisions with the current specification before proposing changes.")
        if additional_blocks:
            approach.append("Use additional context to refine edge cases, acceptance criteria, and integration boundaries.")
        approach.append("Prefer deterministic, modular implementation steps that are easy to validate independently.")
        return approach

    def _derive_design_decisions(self, topic: str, plan_context: str, memory_blocks: List[str], additional_blocks: List[str]) -> List[str]:
        decisions: List[str] = [
            "Keep the implementation modular so each subsystem can be reasoned about and tested in isolation.",
            "Prefer explicit interfaces and data contracts to reduce ambiguity across planning, engineering, and review stages.",
            "Use predictable naming and structure so the generated code integrates cleanly with the rest of the workflow.",
        ]
        if self._extract_key_points(plan_context, limit=1):
            decisions.append("Align design choices directly with the specification rather than introducing unnecessary abstractions.")
        if memory_blocks:
            decisions.append("Preserve relevant prior decisions from memory when they do not conflict with the current plan.")
        if additional_blocks:
            decisions.append("Treat supplemental notes as constraints when they improve feasibility or reduce rework.")
        decisions.append(f"Optimize for a balance of clarity, maintainability, and direct applicability to {topic}.")
        return decisions

    def _derive_trade_offs(self, plan_context: str, memory_blocks: List[str], additional_blocks: List[str]) -> List[str]:
        trade_offs: List[str] = [
            "Speed versus completeness: moving quickly can unblock the workflow, but a more thorough analysis reduces downstream rework.",
            "Simplicity versus extensibility: a smaller design is easier to ship, while a more extensible one may better support future requirements.",
            "Strict adherence to the plan versus adaptive interpretation: fidelity improves consistency, but some flexibility may be needed for missing details.",
        ]
        if memory_blocks or additional_blocks:
            trade_offs.append("Reusing prior context versus re-evaluating assumptions: reuse saves time, but stale assumptions can propagate errors.")
        if self._extract_key_points(plan_context, limit=1):
            trade_offs.append("Narrow scope versus broad coverage: focusing on the highest-value requirements may leave edge cases under-specified.")
        return trade_offs

    def _derive_risks(self, plan_context: str, memory_blocks: List[str], additional_blocks: List[str]) -> List[str]:
        risks: List[str] = [
            "Incomplete specification details may lead to implementation gaps or incorrect defaults.",
            "Hidden dependencies in the workflow can create integration failures if they are not surfaced early.",
            "Ambiguous success criteria may make validation inconsistent across agents.",
        ]
        if memory_blocks:
            risks.append("Historical notes may conflict with current requirements, causing contradictory implementation assumptions.")
        if additional_blocks:
            risks.append("Supplemental constraints may introduce edge cases that affect architecture, validation, or output format.")
        if not plan_context.strip():
            risks.append("Sparse plan context increases the chance that the research plan becomes too generic.")
        return risks

    def _derive_assumptions_and_gaps(self, plan_context: str, memory_blocks: List[str], additional_blocks: List[str]) -> tuple[List[str], List[str]]:
        assumptions = [
            "The current plan/spec is the primary source of truth for expected behavior.",
            "The output will be consumed by downstream agents that benefit from concise, structured guidance.",
        ]
        gaps = [
            "Exact implementation constraints are not fully enumerated in the provided context.",
            "Dependency and integration boundaries may need confirmation before code generation begins.",
        ]
        if memory_blocks:
            assumptions.append("Prior memory/context is relevant and should be treated as advisory unless it conflicts with the latest plan.")
        else:
            gaps.append("No prior memory/context was provided, so historical decisions may be missing.")
        if additional_blocks:
            assumptions.append("Additional context is authoritative for the specific notes it covers.")
        else:
            gaps.append("No additional context was provided to clarify edge cases or non-functional requirements.")
        if not self._extract_key_points(plan_context, limit=1):
            gaps.append("The plan context is sparse, so key requirements may still need to be clarified.")
        return assumptions, gaps

    def _derive_roadmap(self, topic: str, plan_context: str, memory_blocks: List[str], additional_blocks: List[str]) -> List[str]:
        roadmap: List[str] = [
            "1. Re-read the topic, plan, and memory blocks to identify the core objective and any explicit constraints.",
            "2. Extract the most important requirements, dependencies, and output expectations from the available context.",
            "3. Compare the current plan with memory and additional notes to detect conflicts, missing details, or assumptions.",
            "4. Synthesize a recommended technical approach that is directly aligned with the workflow and downstream implementation needs.",
            "5. Convert the findings into actionable implementation steps with clear sequencing and validation checkpoints.",
        ]
        if memory_blocks or additional_blocks:
            roadmap.append("6. Carry forward only the contextual details that are consistent with the current plan and discard unsupported assumptions.")
        else:
            roadmap.append("6. Add explicit follow-up questions or review checkpoints to address missing context before implementation.")
        roadmap.append(f"7. Produce a concise research summary that can guide code generation for {topic} without requiring additional interpretation.")
        return roadmap

    def _run(
        self,
        topic: str,
        plan_context: str,
        memory_context: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> str:
        normalized_topic = (topic or "").strip() or "Untitled topic"
        normalized_plan = self._normalize_text(plan_context)
        normalized_memory = self._normalize_text(memory_context)
        normalized_additional = self._normalize_text(additional_context)

        memory_blocks = self._split_blocks(normalized_memory)
        additional_blocks = self._split_blocks(normalized_additional)

        problem_analysis = self._derive_problem_analysis(normalized_topic, normalized_plan, memory_blocks, additional_blocks)
        technical_approach = self._derive_technical_approach(normalized_topic, normalized_plan, memory_blocks, additional_blocks)
        design_decisions = self._derive_design_decisions(normalized_topic, normalized_plan, memory_blocks, additional_blocks)
        trade_offs = self._derive_trade_offs(normalized_plan, memory_blocks, additional_blocks)
        risks = self._derive_risks(normalized_plan, memory_blocks, additional_blocks)
        assumptions, gaps = self._derive_assumptions_and_gaps(normalized_plan, memory_blocks, additional_blocks)
        roadmap = self._derive_roadmap(normalized_topic, normalized_plan, memory_blocks, additional_blocks)

        sections = [
            "# Deep Research Plan",
            "",
            "## Topic",
            normalized_topic,
            "",
            "## Problem Analysis",
            "\n".join(f"- {item}" for item in problem_analysis),
            "",
            "## Technical Approach",
            "\n".join(f"- {item}" for item in technical_approach),
            "",
            "## Design Decisions",
            "\n".join(f"- {item}" for item in design_decisions),
            "",
            "## Trade-offs",
            "\n".join(f"- {item}" for item in trade_offs),
            "",
            "## Risks",
            "\n".join(f"- {item}" for item in risks),
            "",
            "## Assumptions",
            "\n".join(f"- {item}" for item in assumptions),
            "",
            "## Gaps",
            "\n".join(f"- {item}" for item in gaps),
            "",
            "## Implementation Roadmap",
            "\n".join(f"- {item}" for item in roadmap),
        ]
        return "\n".join(sections).strip()
