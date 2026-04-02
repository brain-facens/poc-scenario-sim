from agents import Agent

from modules.scenario_sim.gen_engine.gen_parts.scene import Scene
from modules.scenario_sim.gen_engine.prompts.scene_prompt import scene_prompt

scene_agent: Agent = Agent(
    name="Scene Writer",
    instructions=scene_prompt,
    output_type=Scene,
)
