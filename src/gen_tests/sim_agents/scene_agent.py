from agents import Agent
from gen_tests.gen_parts.scene import Scene
from gen_tests.prompts.scene_prompt import scene_prompt

scene_agent: Agent = Agent(
    name="Scene Writer",
    instructions=scene_prompt,
    output_type=Scene,
)
