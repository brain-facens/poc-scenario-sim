import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    
    simulation_input_id = Column(String(36), ForeignKey("simulation_inputs.id"), nullable=False)
    
    class_datetime = Column(DateTime(timezone=True))
    class_location = Column(String, index=True)
    scenario_name = Column(String, index=True)
    time_duration = Column(Integer)
    courses = Column(String)
    curricular_unit = Column(String)
    class_code = Column(String)
    class_size = Column(String)
    teacher_name = Column(String)
    class_objectives = Column(String)
    ambience_description = Column(String)
    case_presentation = Column(String)
    student_briefing = Column(String)
    debriefing = Column(String)
    extras = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    simulation_input = relationship("SimulationInput", back_populates="simulations")
    materials = relationship("Material", back_populates="simulation", cascade="all, delete-orphan")
    actors = relationship("Actor", back_populates="simulation", cascade="all, delete-orphan")
    scenes = relationship("Scene", back_populates="simulation", cascade="all, delete-orphan")