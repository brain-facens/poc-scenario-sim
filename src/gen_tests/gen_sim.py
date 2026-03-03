import asyncio
import os

from agents import Runner, set_default_openai_key, trace
from agents.result import RunResult
from dotenv import find_dotenv, load_dotenv

from gen_tests.gen_parts.scenario import Scenario
from gen_tests.sim_agents.scenario_agent import simulation_agent

_ = load_dotenv(dotenv_path=find_dotenv())
assert type(key := os.getenv("OPENAI_KEY")) is str
set_default_openai_key(key=key)


async def generate(usr_input: str) -> Scenario:
    with trace("Simulation Generator"):
        result: RunResult = await Runner.run(
            starting_agent=simulation_agent, input=usr_input
        )
        return result.final_output_as(Scenario)


if __name__ == "__main__":
    # scenario: str = asyncio.run(
    #     generate(
    #         "Escreva uma simulação onde um médico deve realizar um atendimento domiciliar para um idoso com medo de agulhas."
    #     )
    # )

    # scenario = scenario.removeprefix("```html")
    # scenario = scenario.removesuffix("```")

    # if scenario:
    #     _ = HTML(string=scenario).write_pdf("test.pdf")

    # with open("test.txt", "w", encoding="utf-8") as file:
    #     _ = file.write(scenario)

    scenario: Scenario = asyncio.run(
        generate(
            "Escreva uma simulação onde um médico deve realizar um atendimento domiciliar para um idoso com medo de agulhas."
        )
    )

    if scenario:
        with open("test.json", "w", encoding="utf-8") as file:
            _ = file.write(scenario.model_dump_json(indent=4))
