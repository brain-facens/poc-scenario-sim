import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from gen_tests.gen_parts.actor_briefing import ActorBriefing
from gen_tests.gen_parts.participants import Participants
from gen_tests.gen_parts.resource import Resource
from gen_tests.gen_parts.scenario import Scenario
from gen_tests.gen_parts.scene import Scene as GenScene


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
            learning_objectives=str(self.learning_objectives),
            necessary_resources=[
                Resource(name=material.material_name, quantity=material.amount)
                for material in self.materials
            ],
            scene_organization=str(self.scene_organization),
            scene_participants=Participants(
                uses_simulator=int(self.uses_simulator),
                students_quantity=int(self.students_quantity),
                actors_quantity=int(self.actors_quantity),
                students_role=str(self.students_role),
                actors_role=str(self.actors_role),
                simulator_role=str(self.simulator_role),
            ),
            case_presentation=str(self.case_presentation),
            actor_briefing=[
                ActorBriefing(
                    personal_data=actor.personal_data,
                    current_story=actor.current_story,
                    previous_story=actor.previous_story,
                    clothing=actor.clothing,
                    behavior_profile=actor.behavior_profile,
                )
                for actor in self.actors
            ],
            simulator_parameters=str(self.simulator_parameters),
            simulator_evolution_parameters=str(self.simulator_evolution_parameters),
            students_briefing=str(self.students_briefing),
            scene_flow=[
                GenScene(
                    student_role=scene.student_role,
                    actor_sim_role=scene.actor_sim_role,
                    student_plan_b=scene.student_plan_b,
                )
                for scene in self.scenes
            ],
            debriefing=str(self.debriefing),
            appendix=str(self.appendix),
            pdf_path=str(self.pdf_path),
        )
