from agents import Agent
from gen_parts.participants import Participants
from prompts.participants_prompt import participants_prompt

participants_agent: Agent = Agent(
    name="Participants planner",
    instructions=participants_prompt,
    output_type=Participants,
)
