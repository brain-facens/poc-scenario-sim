from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from database import get_db
from schemas.scene_schemas import SceneRead, SceneUpdate
from services.scene_services import update_scene_service, get_scene_by_id_service

scene_router = APIRouter(prefix="/scenes", tags=["scenes"])

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
