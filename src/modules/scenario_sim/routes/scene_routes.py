from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from database import get_db
from modules.scenario_sim.schemas.scene_schemas import SceneCreate, SceneRead, SceneUpdate
from modules.scenario_sim.services.scene_services import (
    create_scene_service,
    delete_scene_service,
    get_scene_by_id_service,
    update_scene_service,
)

scene_router = APIRouter(prefix="/scenes", tags=["scenes"])


@scene_router.post("/", response_model=SceneRead)
def create_scene(
    scene: SceneCreate,
    db: Session = Depends(get_db)
):
    return create_scene_service(db=db, scene_data=scene)


@scene_router.get("/{scene_id}", response_model=SceneRead)
def get_scene(
    scene_id: str = Path(..., description="The ID of the scene to retrieve"),
    db: Session = Depends(get_db)
):
    return get_scene_by_id_service(db=db, scene_id=scene_id)


@scene_router.patch("/{scene_id}", response_model=SceneRead)
def update_scene(
    scene_id: str,
    scene_update: SceneUpdate,
    db: Session = Depends(get_db)
):
    return update_scene_service(db=db, scene_id=scene_id, update_data=scene_update)


@scene_router.delete("/{scene_id}", response_model=SceneRead)
def delete_scene(
    scene_id: str,
    db: Session = Depends(get_db)
):
    return delete_scene_service(db=db, scene_id=scene_id)
