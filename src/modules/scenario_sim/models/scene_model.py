import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Scene(Base):
    __tablename__ = "scenes"

    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )

    student_plan_a = Column(Text)
    actor_sim_directions = Column(Text)
    student_plan_b = Column(Text)

    sequence_number = Column(Integer)

    simulation_id = Column(String(36), ForeignKey("simulations.id"), nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    simulation = relationship("Simulation", back_populates="scenes")
