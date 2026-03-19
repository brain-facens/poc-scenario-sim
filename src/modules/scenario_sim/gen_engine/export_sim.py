from datetime import datetime

from agents import Runner, RunResult
from weasyprint import HTML

from modules.scenario_sim.gen_engine.gen_parts.scenario import Scenario
from modules.scenario_sim.gen_engine.sim_agents.html_agent import html_agent


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

    date: str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    import os
    path: str = f"./pdf_exports/simulação-{date}.pdf"
    abs_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    _ = HTML(string=sim_data).write_pdf(abs_path)
    return abs_path
