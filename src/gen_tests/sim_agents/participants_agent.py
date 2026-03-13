from agents import Agent, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from gen_tests.gen_parts.participants import Participants
from gen_tests.prompts.participants_prompt import participants_prompt

local_client: AsyncOpenAI = AsyncOpenAI(
    base_url="http://localhost:11434/v1", api_key="sk_123"
)

model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="qwen3.5:9b", openai_client=local_client
)

participants_agent: Agent = Agent(
    name="Participants planner",
    instructions=participants_prompt,
    output_type=Participants,
    model="gpt-4o-mini",
)
