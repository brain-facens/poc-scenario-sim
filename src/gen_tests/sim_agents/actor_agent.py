from agents import Agent
from gen_parts.actor_briefing import ActorBriefing
from prompts.actor_prompt import actor_prompt

actor_agent: Agent = Agent(
    name="Actor Briefing",
    instructions=actor_prompt,
    output_type=ActorBriefing,
)
