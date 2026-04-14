import os
from agents import Agent, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from modules.scenario_sim.gen_engine.gen_parts.actor_briefing import ActorBriefing
from modules.scenario_sim.gen_engine.prompts.actor_prompt import actor_prompt

MODEL = os.getenv("LOCAL_MODEL", "qwen3.5:9b")

print(f"using model: {MODEL}")

local_client: AsyncOpenAI = AsyncOpenAI(
    base_url="http://localhost:11434/v1", api_key="sk_123"
)

model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model=MODEL, openai_client=local_client
)

actor_agent: Agent = Agent(
    name="Actor Briefing",
    instructions=actor_prompt,
    output_type=ActorBriefing,
    model=model,
)
