from pydantic import BaseModel


class ActorBriefing(BaseModel):
    personal_data: str
    current_story: str
    previous_story: str
    clothing: str
    behavior_profile: str
