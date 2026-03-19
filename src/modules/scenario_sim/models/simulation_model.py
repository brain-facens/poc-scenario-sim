import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from modules.scenario_sim.gen_engine.gen_parts.actor_briefing import ActorBriefing
from modules.scenario_sim.gen_engine.gen_parts.participants import Participants
from modules.scenario_sim.gen_engine.gen_parts.resource import Resource
from modules.scenario_sim.gen_engine.gen_parts.scenario import Scenario
from modules.scenario_sim.gen_engine.gen_parts.scene import Scene as GenScene


class SimulationStatus(enum.Enum):
    COMPLETE = "complete"
    DOING = "doing"
    INTERRUPTED = "interrupted"
    STALE = "stale"


class PdfStatus(enum.Enum):
    IDLE = "idle"
    GENERATING = "generating"
    READY = "ready"
    ERROR = "error"


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    simulation_input_id = Column(
        String(36), ForeignKey("simulation_inputs.id"), nullable=False
    )

    scene_organization = Column(Text)
    learning_objectives = Column(Text)
    case_presentation = Column(Text)
    students_briefing = Column(Text)
    debriefing = Column(Text)
    appendix = Column(Text)
    pdf_path = Column(String(255), nullable=True)

    uses_simulator = Column(Integer, default=0)
    students_quantity = Column(Integer)
    actors_quantity = Column(Integer)
    students_role = Column(String)
    actors_role = Column(String)
    simulator_role = Column(String)

    simulator_parameters = Column(Text)
    simulator_evolution_parameters = Column(Text)

    status = Column(Enum(SimulationStatus), default=SimulationStatus.DOING, nullable=False)
    pdf_status = Column(Enum(PdfStatus), default=PdfStatus.IDLE, nullable=False)
    error = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    simulation_input = relationship("SimulationInput", back_populates="simulations")
    actors = relationship(
        "Actor", back_populates="simulation", cascade="all, delete-orphan"
    )
    scenes = relationship(
        "Scene", back_populates="simulation", cascade="all, delete-orphan"
    )
    materials = relationship(
        "Material", back_populates="simulation", cascade="all, delete-orphan"
    )

    def to_scenario(self):
        return Scenario(
            learning_objectives=str(self.learning_objectives or ""),
            necessary_resources=[
                Resource(name=material.material_name or "", quantity=material.amount or 0)
                for material in self.materials
            ],
            scene_organization=str(self.scene_organization or ""),
            scene_participants=Participants(
                uses_simulator=bool(self.uses_simulator),
                students_quantity=int(self.students_quantity or 0),
                actors_quantity=int(self.actors_quantity or 0),
                students_role=str(self.students_role or ""),
                actors_role=str(self.actors_role or ""),
                simulator_role=str(self.simulator_role or ""),
            ),
            case_presentation=str(self.case_presentation or ""),
            actor_briefing=[
                ActorBriefing(
                    personal_data=actor.personal_data or "",
                    current_story=actor.current_story or "",
                    previous_story=actor.previous_story or "",
                    clothing=actor.clothing or "",
                    behavior_profile=actor.behavior_profile or "",
                )
                for actor in self.actors
            ],
            simulator_parameters=str(self.simulator_parameters or ""),
            simulator_evolution_parameters=str(self.simulator_evolution_parameters or ""),
            students_briefing=str(self.students_briefing or ""),
            scene_flow=[
                GenScene(
                    student_plan_a=scene.student_plan_a or "",
                    actor_sim_directions=scene.actor_sim_directions or "",
                    student_plan_b=scene.student_plan_b or "",
                )
                for scene in self.scenes
            ],
            debriefing=str(self.debriefing or ""),
            appendix=str(self.appendix or ""),
            pdf_path=str(self.pdf_path or ""),
        )
