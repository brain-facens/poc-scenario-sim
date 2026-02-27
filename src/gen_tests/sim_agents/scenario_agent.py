from agents import Agent, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from gen_tests.gen_parts.scenario import Scenario
from gen_tests.prompts.main_prompt import main_prompt
from gen_tests.sim_agents.actor_agent import actor_agent
from gen_tests.sim_agents.participants_agent import participants_agent
from gen_tests.sim_agents.scene_agent import scene_agent

local_client: AsyncOpenAI = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="sk_123")

model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="qwen3:8b", openai_client=local_client
)

simulation_agent: Agent = Agent(
    name="Simulation Writer",
    instructions=main_prompt,
    output_type=Scenario,
    tools=[
        participants_agent.as_tool(
            tool_name="participants_planner",
            tool_description="Defines number of participants in a scene from students and actors",
        ),
        actor_agent.as_tool(
            tool_name="actor_writer",
            tool_description="Defines actors characteristics and roles",
        ),
        scene_agent.as_tool(
            tool_name="scene_Writer",
            tool_description="Writes scenes based on case and previously generated scenes",
        ),
    ],
    model="gpt-4o-mini",
)
