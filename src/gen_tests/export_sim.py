from datetime import datetime

from agents import Runner, RunResult
from weasyprint import HTML

from gen_tests.gen_parts.scenario import Scenario
from gen_tests.sim_agents.html_agent import html_agent


async def export_pdf(scenario: Scenario) -> bytes | None:
    output: RunResult = await Runner.run(
        starting_agent=html_agent,
        input=scenario.model_dump_json(indent=4),
        context=Scenario,
    )
    sim_data: str = output.final_output_as(str)

    sim_data = sim_data.removeprefix("```html")
    sim_data = sim_data.removesuffix("```")

    date: str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return HTML(string=sim_data).write_pdf(f"./pdf_exports/{date}")
