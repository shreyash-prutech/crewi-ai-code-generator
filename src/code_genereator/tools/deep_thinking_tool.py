from typing import List, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .file_write_tool import FileWriteTool


class DeepThinkingToolInput(BaseModel):
    project_name: Optional[str] = None
    goals: Optional[List[str]] = None
    memories: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    repo_tree: Optional[str] = None
    write_to_file: bool = False
    file_path: Optional[str] = Field(default="dist/plans/deep_thinking_plan.md", description="Relative path for the generated Markdown plan.")

class DeepThinkingTool(BaseTool):
    name: str = "deep_thinking_planner"
    description: str = (
        "Synthesizes memories and context into a detailed Markdown plan. "
        "Optionally writes the plan to disk via FileWriteTool."
    )
    args_schema: Type[BaseModel] = DeepThinkingToolInput

    def _normalize_list(self, items: Optional[List[str]]) -> List[str]:
        if items is None:
            return []
        seen = set()
        normalized = []
        for item in items:
            stripped = item.strip()
            if stripped and stripped not in seen:
                seen.add(stripped)
                normalized.append(stripped)
        return normalized

    def _extract_themes(self, texts: List[str], top_k: int = 8) -> List[str]:
        from collections import Counter
        stopwords = {"and", "or", "the", "a", "an", "in", "on", "at", "to", "for", "with", "by", "of"}
        words = [word.lower() for text in texts for word in text.split() if word.lower() not in stopwords]
        word_counts = Counter(words)
        return [word for word, _ in word_counts.most_common(top_k)]

    def _derive_insights(self, goals: List[str], memories: List[str], requirements: List[str], constraints: List[str]) -> dict:
        insights = {
            "overlaps": [],
            "conflicts": [],
            "key_insights": [],
            "risks": [],
            "mitigations": []
        }
        for goal in goals:
            for memory in memories:
                if goal in memory:
                    insights["overlaps"].append(f"Goal '{goal}' overlaps with memory '{memory}'")
        for req in requirements:
            for con in constraints:
                if req in con:
                    insights["conflicts"].append(f"Requirement '{req}' conflicts with constraint '{con}'")
        insights["key_insights"] = ["Insight 1", "Insight 2"]
        insights["risks"] = ["Risk 1", "Risk 2"]
        insights["mitigations"] = ["Mitigation 1", "Mitigation 2"]
        return insights

    def _propose_architecture(self, repo_tree: Optional[str]) -> List[str]:
        if repo_tree:
            return ["Component 1", "Component 2"]
        return ["src/code_genereator/tools", "dist/plans"]

    def _prioritize_tasks(self, goals: List[str], requirements: List[str], insights: dict) -> List[str]:
        tasks = ["Planning", "Design", "Implementation", "Validation", "Delivery"]
        if insights["conflicts"]:
            tasks.insert(0, "Resolve Conflicts")
        return tasks

    def _generate_markdown_plan(self, project_name: Optional[str], goals: List[str], memories: List[str], requirements: List[str], constraints: List[str], repo_tree: Optional[str], insights: dict, architecture: List[str], tasks: List[str]) -> str:
        plan = f"# {project_name or 'Deep Thinking Plan'}\n\n"
        plan += "## Context\n"
        plan += "### Goals\n" + "\n".join(f"- {goal}" for goal in goals) + "\n"
        plan += "### Requirements\n" + "\n".join(f"- {req}" for req in requirements) + "\n"
        plan += "### Constraints\n" + "\n".join(f"- {con}" for con in constraints) + "\n"
        plan += "## Repo Snapshot\n" + (repo_tree or "No repo tree provided") + "\n"
        plan += "## Memory Insights\n"
        plan += "### Themes\n" + "\n".join(f"- {theme}" for theme in insights["key_insights"]) + "\n"
        plan += "### Overlaps\n" + "\n".join(f"- {overlap}" for overlap in insights["overlaps"]) + "\n"
        plan += "### Conflicts\n" + "\n".join(f"- {conflict}" for conflict in insights["conflicts"]) + "\n"
        plan += "## Architecture Outline\n" + "\n".join(f"- {comp}" for comp in architecture) + "\n"
        plan += "## Implementation Plan\n" + "\n".join(f"- {task}" for task in tasks) + "\n"
        plan += "## Risks and Mitigations\n"
        plan += "### Risks\n" + "\n".join(f"- {risk}" for risk in insights["risks"]) + "\n"
        plan += "### Mitigations\n" + "\n".join(f"- {mitigation}" for mitigation in insights["mitigations"]) + "\n"
        plan += "## Deliverables\n"
        plan += f"- Plan saved to: {file_path}\n" if write_to_file else "- Plan not saved to file\n"
        return plan

    def _run(self, project_name: Optional[str] = None, goals: Optional[List[str]] = None, memories: Optional[List[str]] = None, requirements: Optional[List[str]] = None, constraints: Optional[List[str]] = None, repo_tree: Optional[str] = None, write_to_file: bool = False, file_path: Optional[str] = None) -> str:
        goals = self._normalize_list(goals)
        memories = self._normalize_list(memories)
        requirements = self._normalize_list(requirements)
        constraints = self._normalize_list(constraints)
        themes = self._extract_themes(memories)
        insights = self._derive_insights(goals, memories, requirements, constraints)
        architecture = self._propose_architecture(repo_tree)
        tasks = self._prioritize_tasks(goals, requirements, insights)
        markdown_content = self._generate_markdown_plan(project_name, goals, memories, requirements, constraints, repo_tree, insights, architecture, tasks)
        if write_to_file:
            file_write_tool = FileWriteTool()
            file_write_tool._run(file_path or "dist/plans/deep_thinking_plan.md", markdown_content)
            return f"Plan saved to {file_path or 'dist/plans/deep_thinking_plan.md'}\n\n{markdown_content}"
        return markdown_content
