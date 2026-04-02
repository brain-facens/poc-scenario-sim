from agents import Agent

from modules.scenario_sim.gen_engine.gen_parts.actor_briefing import ActorBriefing
from modules.scenario_sim.gen_engine.prompts.actor_prompt import actor_prompt

actor_agent: Agent = Agent(
    name="Actor Briefing",
    instructions=actor_prompt,
    output_type=ActorBriefing,
)
