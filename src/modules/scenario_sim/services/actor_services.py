from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from modules.scenario_sim.models.actor_model import Actor
from modules.scenario_sim.schemas.actor_schemas import ActorCreate, ActorUpdate


def create_actor_service(db: Session, actor_data: ActorCreate):
    db_actor = Actor(**actor_data.model_dump())
    db.add(db_actor)
    db.commit()
    db.refresh(db_actor)
    return db_actor


def get_actor_by_id_service(db: Session, actor_id: str):
    actor = db.query(Actor).filter(Actor.id == actor_id).first()
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with id {actor_id} not found"
        )
    return actor


def update_actor_service(db: Session, actor_id: str, update_data: ActorUpdate):
    db_actor = get_actor_by_id_service(db, actor_id)

    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(db_actor, key, value)

    db.commit()
    db.refresh(db_actor)
    return db_actor


def delete_actor_service(db: Session, actor_id: str):
    db_actor = get_actor_by_id_service(db, actor_id)
    db.delete(db_actor)
    db.commit()
    return db_actor
