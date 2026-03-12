from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.scene_model import Scene
from schemas.scene_schemas import SceneUpdate

def get_scene_by_id_service(db: Session, scene_id: str):
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene with id {scene_id} not found"
        )
    return scene

def update_scene_service(db: Session, scene_id: str, update_data: SceneUpdate):
    db_scene = get_scene_by_id_service(db, scene_id)
    
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for key, value in update_dict.items():
        setattr(db_scene, key, value)
    
    db.commit()
    db.refresh(db_scene)
    return db_scene
