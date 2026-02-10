from typing import List, Optional, Type, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepThinkingToolInput(BaseModel):
    goals: List[str] = Field(default_factory=list, description="High-level goals or outcomes for the task or feature.")
    context: Optional[str] = Field(None, description="Problem context, repo info, or relevant description.")
    constraints: List[str] = Field(default_factory=list, description="Constraints such as time, security, compatibility, or architectural boundaries.")
    memories: Union[str, List[str], None] = Field(None, description="Memory entries to reflect on. Either a single newline-separated string or a list of memory notes.")
    sections: List[str] = Field(default_factory=lambda: ["Summary", "Memory Insights", "Plan", "Implementation", "File Impact", "API Design", "Validation", "Risks", "Next Steps"], description="Sections to include in the generated Markdown plan.")

class DeepThinkingTool(BaseTool):
    name: str = "Deep Thinking Planner"
    description: str = "Generates a structured Markdown planning and implementation document by deeply reflecting on provided memories, context, goals, and constraints. Use this before coding to align on approach and risks."
    args_schema: Type[BaseModel] = DeepThinkingToolInput

    def _run(self, goals: List[str], context: Optional[str], constraints: List[str], memories: Union[str, List[str], None], sections: List[str]) -> str:
        memories_list = self._normalize_memories(memories)
        key_sentences = self._extract_key_sentences(memories_list)
        themes = self._derive_themes(memories_list)
        risks = self._derive_risks(themes, key_sentences, constraints)
        actionables = self._derive_actionables(key_sentences, themes)
        return self._build_markdown(sections, goals, context, constraints, themes, key_sentences, actionables, risks)

    def _normalize_memories(self, memories: Union[str, List[str], None]) -> List[str]:
        if isinstance(memories, str):
            entries = [entry.strip() for entry in memories.split('\n') if entry.strip()]
            return [sentence.strip() for entry in entries for sentence in entry.split('.') if sentence.strip()]
        elif isinstance(memories, list):
            return [entry.strip() for entry in memories if entry.strip()]
        return []

    def _tokenize(self, text: str) -> List[str]:
        stopwords = {"a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"}
        tokens = text.lower().replace('.', '').replace(',', '').replace('!', '').replace('?', '').split()
        return [token for token in tokens if token not in stopwords and len(token) > 2]

    def _extract_key_sentences(self, entries: List[str]) -> List[str]:
        key_markers = ["learn", "lesson", "should", "avoid", "bug", "fail", "fix", "broke", "deprecated", "regression", "risk", "mitigate"]
        sentences = [sentence.strip() for entry in entries for sentence in entry.split('. ') if any(marker in sentence for marker in key_markers)]
        return sentences

    def _derive_themes(self, entries: List[str], top_n: int = 5) -> List[str]:
        from collections import Counter
        all_tokens = [token for entry in entries for token in self._tokenize(entry)]
        most_common = Counter(all_tokens).most_common(top_n)
        return [token for token, _ in most_common]

    def _derive_risks(self, themes: List[str], key_sentences: List[str], constraints: List[str]) -> List[str]:
        risks = [f"Theme '{theme}' may be impacted by constraint '{constraint}'" for theme in themes for constraint in constraints]
        risks += [f"Potential gaps regarding '{theme}' due to historical issues: {sentence}" for theme in themes for sentence in key_sentences]
        return risks

    def _derive_actionables(self, key_sentences: List[str], themes: List[str]) -> List[str]:
        actionables = [sentence for sentence in key_sentences if any(keyword in sentence for keyword in ["should", "avoid", "fix", "ensure"])]
        if not actionables:
            actionables = [f"Investigate {theme}" for theme in themes]
        return actionables

    def _build_markdown(self, sections: List[str], goals: List[str], context: Optional[str], constraints: List[str], themes: List[str], key_sentences: List[str], actionables: List[str], risks: List[str]) -> str:
        md = []
        if "Summary" in sections:
            md.append("# Summary")
            md.append(f"## Context\n{context}\n" if context else "")
            md.append(f"## Goals\n- " + "\n- ".join(goals) + "\n")
        if "Memory Insights" in sections:
            md.append("# Memory Insights")
            md.append("## Recurring Themes\n- " + "\n- ".join(themes) + "\n")
            md.append("## Key Lessons\n- " + "\n- ".join(key_sentences) + "\n")
            md.append("## Actionable Items\n- " + "\n- ".join(actionables) + "\n")
        if "Plan" in sections:
            md.append("# Plan")
            md.append("## Objectives\n- " + "\n- ".join(goals) + "\n")
            md.append("## Scope and Assumptions\n- " + "\n- ".join(constraints) + "\n")
            md.append("## Phased Plan\n- Discover\n- Design\n- Implement\n- Validate\n")
        if "Implementation" in sections:
            md.append("# Implementation")
            md.append("## Steps\n1. Normalize inputs\n2. Analyze memories\n3. Build Markdown plan\n")
        if "File Impact" in sections:
            md.append("# File Impact")
            md.append("- src/code_genereator/tools/deep_thinking_tool.py\n- src/code_genereator/tools/__init__.py\n")
        if "API Design" in sections:
            md.append("# API Design")
            md.append("## Tool Name\nDeep Thinking Planner\n")
            md.append("## Description\nGenerates a structured Markdown planning and implementation document by deeply reflecting on provided memories, context, goals, and constraints.\n")
            md.append("## Args Schema\n- goals: List[str]\n- context: Optional[str]\n- constraints: List[str]\n- memories: Union[str, List[str], None]\n- sections: List[str]\n")
            md.append("## _run Signature\n_run(self, goals: List[str], context: Optional[str], constraints: List[str], memories: Union[str, List[str], None], sections: List[str]) -> str\n")
        if "Validation" in sections:
            md.append("# Validation")
            md.append("## Manual Checks\n- Verify Markdown structure\n- Validate content relevance\n")
            md.append("## Unit Tests\n- Test normalization of memories\n- Test extraction of key sentences\n- Test derivation of themes\n- Test risk formulation\n- Test actionable item generation\n")
        if "Risks" in sections:
            md.append("# Risks")
            md.append("- " + "\n- ".join(risks) + "\n")
        if "Next Steps" in sections:
            md.append("# Next Steps")
            md.append("- " + "\n- ".join(actionables) + "\n")
        return "\n".join(md)

    """
    Example usage:
    from src.code_genereator.tools import DeepThinkingTool
    tool = DeepThinkingTool()
    md = tool.run({
        "goals": ["Add deep-thinking tool"],
        "context": "CrewAI code generator",
        "memories": ["We previously broke __init__ export", "Should avoid adding dependencies"],
        "constraints": ["No extra deps"]
    })
    """
