import os
from typing import Dict, List

import yaml

from .file_write_tool import FileWriteTool, FileWriteToolInput


class DeepResearchTool:
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), '../config/tasks.yaml'), 'r') as file:
            self.config = yaml.safe_load(file)

    def gather_data(self, topic: str) -> List[str]:
        data = ["data_point_{}".format(i) for i in range(10)]
        return data

    def analyze_data(self, data: List[str]) -> Dict[str, str]:
        analysis = {item: "analysis_of_{}".format(item) for item in data}
        return analysis

    def identify_gaps(self, analysis: Dict[str, str]) -> List[str]:
        gaps = ["gap_detected_in_{}".format(key) for key, value in analysis.items() if "gap" in value]
        return gaps

    def synthesize_findings(self, analysis: Dict[str, str], gaps: List[str]) -> str:
        findings = "\n".join(["## Analysis\n"] + [f"{key}: {value}" for key, value in analysis.items()] +
                             ["\n## Gaps\n"] + [gap for gap in gaps])
        return findings

    def generate_markdown(self, findings: str, file_path: str):
        file_writer = FileWriteTool()
        input_data = FileWriteToolInput(file_path=file_path, content=findings)
        return file_writer._run(**input_data.dict())
