from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from database import get_db
from schemas.material_schemas import MaterialRead, MaterialUpdate
from services.material_services import update_material_service, get_material_by_id_service

material_router = APIRouter(prefix="/materials", tags=["materials"])

@material_router.get("/{material_id}", response_model=MaterialRead)
def get_material(
    material_id: str = Path(..., description="The ID of the material to retrieve"),
    db: Session = Depends(get_db)
):
    return get_material_by_id_service(db=db, material_id=material_id)

@material_router.patch("/{material_id}", response_model=MaterialRead)
def update_material(
    material_id: str,
    material_update: MaterialUpdate,
    db: Session = Depends(get_db)
):
    return update_material_service(db=db, material_id=material_id, update_data=material_update)
