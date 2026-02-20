from agents import Agent
from gen_parts.scenario import Scenario
from prompts.main_prompt import main_prompt
from sim_agents.actor_agent import actor_agent
from sim_agents.participants_agent import participants_agent
from sim_agents.scene_agent import scene_agent

simulation_agent: Agent = Agent(
    name="Simulation Writer",
    instructions=main_prompt,
    output_type=Scenario,
    tools=[
        participants_agent.as_tool(
            tool_name="participants_planner",
            tool_description="Defines number of participants in a scene from students and actors",
        ),
        actor_agent.as_tool(
            tool_name="actor_writer",
            tool_description="Defines actors characteristics and roles",
        ),
        scene_agent.as_tool(
            tool_name="scene_Writer",
            tool_description="Writes scenes based on case and previously generated scenes",
        ),
    ],
)
