from agents import Agent
from gen_tests.gen_parts.actor_briefing import ActorBriefing
from gen_tests.prompts.actor_prompt import actor_prompt

actor_agent: Agent = Agent(
    name="Actor Briefing",
    instructions=actor_prompt,
    output_type=ActorBriefing,
)
