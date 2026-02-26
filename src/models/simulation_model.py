import uuid
import enum
from sqlalchemy import Column, Enum, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class SimulationStatus(enum.Enum):
    COMPLETE = "complete"
    DOING = "doing"
    INTERRUPTED = "interrupted"
    STALE = "stale"

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    simulation_input_id = Column(String(36), ForeignKey("simulation_inputs.id"), nullable=False)

    scene_organization = Column(Text) 
    case_presentation = Column(Text)
    students_briefing = Column(Text)
    debriefing = Column(Text)
    appendix = Column(Text)
    
    uses_simulator = Column(Integer, default=0)
    students_quantity = Column(Integer)
    actors_quantity = Column(Integer)
    students_role = Column(String)
    actors_role = Column(String)
    simulator_role = Column(String)

    simulator_parameters = Column(Text)
    simulator_evolution_parameters = Column(Text)
    
    status = Column(Enum(SimulationStatus), default=SimulationStatus.DOING, nullable=False)
    error = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    simulation_input = relationship("SimulationInput", back_populates="simulations")
    actors = relationship("Actor", back_populates="simulation", cascade="all, delete-orphan")
    scenes = relationship("Scene", back_populates="simulation", cascade="all, delete-orphan")