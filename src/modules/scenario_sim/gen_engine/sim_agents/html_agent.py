
import os

from agents import Agent, FileSearchTool, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from modules.scenario_sim.gen_engine.gen_parts.scenario import Scenario
from modules.scenario_sim.gen_engine.prompts.html_prompt import html_prompt

MODEL = os.getenv("LOCAL_MODEL", "gemma2:9b")

local_client: AsyncOpenAI = AsyncOpenAI(
    base_url="http://localhost:11434/v1", api_key="sk_123"
)

model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model=MODEL, openai_client=local_client
)

html_agent: Agent = Agent[Scenario](
    name="Actor Briefing",
    instructions=html_prompt,
    model=model,  # "gpt-5-mini"
)
