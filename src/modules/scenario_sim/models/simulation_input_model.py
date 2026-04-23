import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class SimulationInput(Base):
    __tablename__ = "simulation_inputs"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    pitch = Column(String, index=True, nullable=False)
    local_aula = Column(String, nullable=False)
    nome_cenario = Column(String, nullable=False)
    cursos = Column(String, nullable=False)
    componente_curricular = Column(String, nullable=False)
    student_ammount = Column(Integer, nullable=False)
    actors_ammount = Column(Integer, nullable=False)
    uses_simulator = Column(Boolean, nullable=False, default=False)
    simulator_description = Column(Text, nullable=True)
    
    objectives = relationship("SimulationInputObjective", back_populates="simulation_input", cascade="all, delete-orphan")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    simulations = relationship("Simulation", back_populates="simulation_input")


class SimulationInputObjective(Base):
    __tablename__ = "simulation_input_objectives"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    description = Column(Text, nullable=False)
    simulation_input_id = Column(String(36), ForeignKey("simulation_inputs.id"), nullable=False)

    simulation_input = relationship("SimulationInput", back_populates="objectives")
