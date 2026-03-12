from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from database import get_db
from schemas.actor_schemas import ActorRead, ActorUpdate
from services.actor_services import update_actor_service, get_actor_by_id_service

actor_router = APIRouter(prefix="/actors", tags=["actors"])

@actor_router.get("/{actor_id}", response_model=ActorRead)
def get_actor(
    actor_id: str = Path(..., description="The ID of the actor to retrieve"),
    db: Session = Depends(get_db)
):
    return get_actor_by_id_service(db=db, actor_id=actor_id)

@actor_router.patch("/{actor_id}", response_model=ActorRead)
def update_actor(
    actor_id: str,
    actor_update: ActorUpdate,
    db: Session = Depends(get_db)
):
    return update_actor_service(db=db, actor_id=actor_id, update_data=actor_update)
