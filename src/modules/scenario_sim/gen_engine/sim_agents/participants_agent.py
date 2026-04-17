from agents import Agent

from modules.scenario_sim.gen_engine.gen_parts.participants import Participants
from modules.scenario_sim.gen_engine.prompts.participants_prompt import (
    participants_prompt,
)

participants_agent: Agent = Agent(
    name="Participants planner",
    instructions=participants_prompt,
    output_type=Participants,
)
