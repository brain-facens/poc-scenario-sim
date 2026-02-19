import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Actor(Base):
    __tablename__ = "actors"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    
    personal_data = Column(String)
    current_history = Column(String)
    previous_history = Column(String)
    clothing = Column(String)
    behavior_profile = Column(String)

    simulation_id = Column(String(36), ForeignKey("simulations.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    simulation = relationship("Simulation", back_populates="actors")