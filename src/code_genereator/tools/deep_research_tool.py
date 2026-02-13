import markdown
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepResearchInput(BaseModel):
    context: str = Field(..., description="Contextual information necessary for research.")
    requirements: str = Field(..., description="Specific requirements for the research.")

class DeepResearchTool(BaseTool):
    name: str = "Deep Research Tool"
    description: str = "Performs deep research to generate a structured Markdown document outlining the research process."
    args_schema: Type[BaseModel] = DeepResearchInput

    def _run(self, context: str, requirements: str) -> str:
        data = self.gather_context(context)
        analyzed_data = self.analyze_data(data)
        gaps = self.identify_gaps(analyzed_data)
        findings = self.synthesize_findings(analyzed_data, gaps)
        markdown_report = self.generate_markdown(findings)
        return markdown_report

    def gather_context(self, context: str) -> dict:
        return {"data": context}

    def analyze_data(self, data: dict) -> dict:
        return {"analyzed": data}

    def identify_gaps(self, analyzed_data: dict) -> list:
        return ["gap1", "gap2"]

    def synthesize_findings(self, analyzed_data: dict, gaps: list) -> dict:
        return {"findings": analyzed_data, "gaps": gaps}

    def generate_markdown(self, findings: dict) -> str:
        md = markdown.Markdown()
        report = md.convert(str(findings))
        with open("research_report.md", "w") as file:
            file.write(report)
        return "research_report.md"
