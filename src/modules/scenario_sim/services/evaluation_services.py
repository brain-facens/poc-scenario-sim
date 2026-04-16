from sqlalchemy.orm import Session
from modules.scenario_sim.models.evaluation_model import Evaluation
from modules.scenario_sim.schemas.evaluation_schema import EvaluationCreate, EvaluationUpdate
from typing import List, Optional

def create_evaluation(db: Session, evaluation: EvaluationCreate, user_id: str) -> Evaluation:
    db_evaluation = Evaluation(
        simulation_id=evaluation.simulation_id,
        user_id=user_id,
        explanation=evaluation.explanation,
        grade=evaluation.grade
    )
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation

def get_evaluation(db: Session, evaluation_id: str) -> Optional[Evaluation]:
    return db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()

def get_evaluations_by_simulation(db: Session, simulation_id: str) -> List[Evaluation]:
    return db.query(Evaluation).filter(Evaluation.simulation_id == simulation_id).all()

def update_evaluation(db: Session, evaluation_id: str, evaluation_update: EvaluationUpdate) -> Optional[Evaluation]:
    db_evaluation = get_evaluation(db, evaluation_id)
    if not db_evaluation:
        return None
    
    update_data = evaluation_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_evaluation, key, value)
    
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation

def delete_evaluation(db: Session, evaluation_id: str) -> bool:
    db_evaluation = get_evaluation(db, evaluation_id)
    if not db_evaluation:
        return False
    
    db.delete(db_evaluation)
    db.commit()
    return True
