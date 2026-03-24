from agents import Agent, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from modules.scenario_sim.gen_engine.gen_parts.scene import Scene
from modules.scenario_sim.gen_engine.prompts.scene_prompt import scene_prompt

local_client: AsyncOpenAI = AsyncOpenAI(
    base_url="http://localhost:11434/v1", api_key="sk_123"
)

model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="qwen3.5:9b", openai_client=local_client
)

scene_agent: Agent = Agent(
    name="Scene Writer",
    instructions=scene_prompt,
    output_type=Scene,
    model="gpt-5-mini",
)
