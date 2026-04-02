import asyncio
import os

from agents import ModelSettings, RunConfig, Runner, set_default_openai_key, trace
from agents.result import RunResult
from dotenv import find_dotenv, load_dotenv
from openai.types import Reasoning

from modules.scenario_sim.gen_engine.gen_parts.scenario import Scenario
from modules.scenario_sim.gen_engine.local_model import model
from modules.scenario_sim.gen_engine.log_saver import log_exception
from modules.scenario_sim.gen_engine.sim_agents.scenario_agent import simulation_agent

_ = load_dotenv(dotenv_path=find_dotenv())
assert type(key := os.getenv("OPENAI_KEY")) is str
set_default_openai_key(key=key)


async def generate(usr_input: str) -> Scenario:
    with trace("Simulation Generator"):
        result: RunResult
        try:
            result = await Runner.run(
                starting_agent=simulation_agent,
                input=usr_input,
                run_config=RunConfig(
                    model="gpt-5-nano",
                    model_settings=ModelSettings(
                        reasoning=Reasoning(effort="low"),
                    ),
                ),
            )
            return result.final_output_as(Scenario)

        except Exception as ex:
            print("Openai generation failed, trying with local model...")
            log_exception(ex)

            result = await Runner.run(
                starting_agent=simulation_agent,
                input=usr_input,
                run_config=RunConfig(model=model),
            )
            return result.final_output_as(Scenario)


if __name__ == "__main__":
    from modules.scenario_sim.gen_engine.export_sim import export_pdf

    scenario: Scenario = asyncio.run(
        generate(
            "Escreva uma simulação onde um médico deve realizar um atendimento domiciliar para um idoso com medo de agulhas."
        )
    )

    if scenario:
        with open("test.json", "w", encoding="utf-8") as file:
            _ = file.write(scenario.model_dump_json(indent=4))

        asyncio.run(export_pdf(scenario))
