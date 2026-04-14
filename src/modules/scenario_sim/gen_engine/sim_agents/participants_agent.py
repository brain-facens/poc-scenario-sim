import os
from agents import Agent, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from modules.scenario_sim.gen_engine.gen_parts.participants import Participants
from modules.scenario_sim.gen_engine.prompts.participants_prompt import (
    participants_prompt,
)

MODEL = os.getenv("LOCAL_MODEL", "qwen3.5:9b")

local_client: AsyncOpenAI = AsyncOpenAI(
    base_url="http://localhost:11434/v1", api_key="sk_123"
)

model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model=MODEL, openai_client=local_client
)

participants_agent: Agent = Agent(
    name="Participants planner",
    instructions=participants_prompt,
    output_type=Participants,
    model=model,
)
