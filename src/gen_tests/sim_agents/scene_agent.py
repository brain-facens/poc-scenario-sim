from agents import Agent
from gen_parts.scene import Scene
from prompts.scene_prompt import scene_prompt

scene_agent: Agent = Agent(
    name="Scene Writer",
    instructions=scene_prompt,
    output_type=Scene,
)
