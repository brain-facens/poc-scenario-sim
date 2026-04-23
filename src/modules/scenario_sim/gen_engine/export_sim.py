import os
from datetime import datetime

from modules.scenario_sim.gen_engine.docx_generator import DocxGenerator
from modules.scenario_sim.gen_engine.gen_parts.scenario import Scenario


def path_builder(*, format: str = ".pdf") -> str:
    date: str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    path: str = f"./pdf_exports/simulação-{date}{format}"
    abs_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path


async def export_docx(scenario: Scenario) -> str:
    abs_path = path_builder(format=".docx")
    docx = DocxGenerator()
    return docx.generate(scenario, abs_path)
