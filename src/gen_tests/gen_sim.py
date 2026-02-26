import asyncio

from agents import Runner, trace
from agents.result import RunResult
from gen_parts.scenario import Scenario
from sim_agents.html_agent import html_agent
from sim_agents.scenario_agent import simulation_agent
from weasyprint import HTML

# _ = load_dotenv(dotenv_path=find_dotenv())
# assert type(key := os.getenv("OPENAI_KEY")) is str
# set_default_openai_key(key=key)

# agent = Agent(name="Assistant", instructions="You are a helpfull assistant")


async def generate(usr_input: str) -> str:
    with trace("Simulation Generator"):
        result: RunResult = await Runner.run(starting_agent=simulation_agent, input=usr_input)
        result_data: Scenario = result.final_output_as(Scenario)
        output: RunResult = await Runner.run(
            starting_agent=html_agent,
            input=result_data.model_dump_json(indent=4),
            context=result.final_output_as(Scenario),
        )
        return output.final_output


if __name__ == "__main__":
    scenario: str = asyncio.run(
        generate(
            "Escreva uma simulação onde um médico deve realizar um atendimento domiciliar para um idoso com medo de agulhas."
        )
    )

    if scenario:
        _ = HTML(string=scenario).write_pdf("test.pdf")

        # with open("test.txt", "w", encoding="utf-8") as file:
        #     _ = file.write(scenario)

    # scenario: Scenario = asyncio.run(
    #     generate(
    #         "Escreva uma simulação onde um médico deve realizar um atendimento domiciliar para um idoso com medo de agulhas."
    #     )
    # )

    # if scenario:
    #     with open("test.json", "w", encoding="utf-8") as file:
    #         _ = file.write(scenario.model_dump_json(indent=4))
