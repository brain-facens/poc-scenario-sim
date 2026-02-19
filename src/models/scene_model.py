import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Scene(Base):
    __tablename__ = "scenes"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    
    name = Column(String, nullable=False)
    description = Column(Text)
    
    simulation_id = Column(String(36), ForeignKey("simulations.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    simulation = relationship("Simulation", back_populates="scenes")