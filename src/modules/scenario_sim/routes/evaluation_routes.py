from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from core.security import get_current_user
from modules.auth.models.user_model import User
from modules.scenario_sim.schemas.evaluation_schema import EvaluationCreate, EvaluationResponse, EvaluationUpdate
from modules.scenario_sim.services.evaluation_services import (
    create_evaluation,
    get_evaluation,
    get_evaluations_by_simulation,
    update_evaluation,
    delete_evaluation
)

evaluation_router = APIRouter(prefix="/evaluations", tags=["evaluations"])

@evaluation_router.post("/", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
def post_evaluation(
    evaluation: EvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new evaluation for a simulation.
    """
    return create_evaluation(db=db, evaluation=evaluation, user_id=current_user.id)

@evaluation_router.get("/simulation/{simulation_id}", response_model=List[EvaluationResponse])
def list_evaluations_by_simulation(
    simulation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lists all evaluations for a specific simulation.
    """
    return get_evaluations_by_simulation(db=db, simulation_id=simulation_id)

@evaluation_router.get("/{evaluation_id}", response_model=EvaluationResponse)
def read_evaluation(
    evaluation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a specific evaluation by ID.
    """
    db_evaluation = get_evaluation(db=db, evaluation_id=evaluation_id)
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return db_evaluation

@evaluation_router.patch("/{evaluation_id}", response_model=EvaluationResponse)
def patch_evaluation(
    evaluation_id: str,
    evaluation_update: EvaluationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates an existing evaluation.
    Only the creator of the evaluation (or potentially an admin) should be able to update it.
    """
    db_evaluation = get_evaluation(db=db, evaluation_id=evaluation_id)
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    if db_evaluation.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this evaluation")
        
    return update_evaluation(db=db, evaluation_id=evaluation_id, evaluation_update=evaluation_update)

@evaluation_router.delete("/{evaluation_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_evaluation(
    evaluation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes an evaluation.
    """
    db_evaluation = get_evaluation(db=db, evaluation_id=evaluation_id)
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    if db_evaluation.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this evaluation")
        
    delete_evaluation(db=db, evaluation_id=evaluation_id)
    return None
