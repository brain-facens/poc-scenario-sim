import os
from datetime import datetime

from agents import Runner, RunResult
from weasyprint import HTML

from modules.scenario_sim.gen_engine.gen_parts.scenario import Scenario
from modules.scenario_sim.gen_engine.sim_agents.html_agent import html_agent
from modules.scenario_sim.services.scenario_docx_service import save_scenario_docx


def path_builder(*, format: str = ".pdf") -> str:
    date: str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    path: str = f"./pdf_exports/simulação-{date}{format}"
    abs_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path


async def export_pdf(scenario: Scenario) -> str:
    for i, tool in enumerate(html_agent.tools):
        print(f"Tool {i}: {tool}")

    output: RunResult = await Runner.run(
        starting_agent=html_agent,
        input=scenario.model_dump_json(indent=4),
        context=Scenario,
    )
    sim_data: str = output.final_output_as(str)

    sim_data = sim_data.removeprefix("```html")
    sim_data = sim_data.removesuffix("```")

    abs_path = path_builder()
    _ = HTML(string=sim_data).write_pdf(abs_path)
    return abs_path


async def export_docx(scenario: Scenario) -> str:
    abs_path = path_builder(format=".docx")
    return save_scenario_docx(scenario, abs_path)
