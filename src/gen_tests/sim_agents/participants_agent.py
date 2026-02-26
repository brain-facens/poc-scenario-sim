from agents import Agent
from gen_tests.gen_parts.participants import Participants
from gen_tests.prompts.participants_prompt import participants_prompt

participants_agent: Agent = Agent(
    name="Participants planner",
    model="gpt-4o-mini",
    instructions=participants_prompt,
    output_type=Participants,
)