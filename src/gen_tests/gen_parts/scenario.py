from pydantic import BaseModel

from .actor_briefing import ActorBriefing
from .participants import Participants
from .scene import Scene


class Scenario(BaseModel):
    scene_organization: str
    scene_participants: Participants
    case_presentation: str
    actor_briefing: list[ActorBriefing]
    simulator_parameters: str
    simulator_evolution_parameters: str
    students_briefing: str
    scene_flow: list[Scene]
    debriefing: str
    appendix: str
