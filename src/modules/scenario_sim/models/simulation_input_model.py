import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class SimulationInput(Base):
    __tablename__ = "simulation_inputs"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    pitch = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    simulations = relationship("Simulation", back_populates="simulation_input")
