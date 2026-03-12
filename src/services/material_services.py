from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.material_model import Material
from schemas.material_schemas import MaterialUpdate

def get_material_by_id_service(db: Session, material_id: str):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material with id {material_id} not found"
        )
    return material

def update_material_service(db: Session, material_id: str, update_data: MaterialUpdate):
    db_material = get_material_by_id_service(db, material_id)
    
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for key, value in update_dict.items():
        setattr(db_material, key, value)
    
    db.commit()
    db.refresh(db_material)
    return db_material
