import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Material(Base):
    __tablename__ = "materials"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    
    material_name = Column(String, nullable=False)
    amount = Column(Integer, default=1)
    
    simulation_id = Column(String(36), ForeignKey("simulations.id"), nullable=False)
        
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    simulation = relationship("Simulation", back_populates="materials")
