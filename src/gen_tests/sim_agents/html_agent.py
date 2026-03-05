from agents import Agent, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from gen_tests.gen_parts.scenario import Scenario
from gen_tests.prompts.html_prompt import html_prompt

local_client: AsyncOpenAI = AsyncOpenAI(
    base_url="http://localhost:11434/v1", api_key="sk_123"
)

model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="qwen3:8b", openai_client=local_client
)

html_agent: Agent = Agent[Scenario](
    name="Actor Briefing",
    instructions=html_prompt,
    model="gpt-4o-mini",
)
