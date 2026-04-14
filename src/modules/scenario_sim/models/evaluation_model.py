import uuid
from sqlalchemy import Column, ForeignKey, String, Text, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    simulation_id = Column(String(36), ForeignKey("simulations.id"), nullable=False)
    explanation = Column(Text, nullable=False)
    grade = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")
    simulation = relationship("Simulation", back_populates="evaluations")
