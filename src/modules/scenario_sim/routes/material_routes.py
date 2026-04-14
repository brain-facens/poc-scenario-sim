from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from database import get_db
from modules.scenario_sim.schemas.material_schemas import MaterialCreate, MaterialRead, MaterialUpdate
from modules.scenario_sim.services.material_services import (
    create_material_service,
    delete_material_service,
    get_material_by_id_service,
    update_material_service,
)

material_router = APIRouter(prefix="/materials", tags=["materials"])


@material_router.post("/", response_model=MaterialRead)
def create_material(
    material: MaterialCreate,
    db: Session = Depends(get_db)
):
    return create_material_service(db=db, material_data=material)


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


@material_router.delete("/{material_id}", response_model=MaterialRead)
def delete_material(
    material_id: str,
    db: Session = Depends(get_db)
):
    return delete_material_service(db=db, material_id=material_id)
