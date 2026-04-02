import math
from typing import Generic, TypeVar, List, Type, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    limit: int
    total_pages: int
    items: List[T]

def paginate_and_filter(
    db: Session,
    model: Type[Any],
    page: int,
    limit: int,
    filters: dict,
    default_order_by=None,
    query=None
) -> dict:
    if query is None:
        query = db.query(model)
    
    for key, value in filters.items():
        if value is not None and value != "":
            column = getattr(model, key, None)
            # Support basic string searching or exact match for enums/booleans
            if column is not None:
                # If it's a string, use ilike for partial matching
                if hasattr(column.type, "length") or str(column.type) == "VARCHAR" or str(column.type) == "TEXT":
                    query = query.filter(column.ilike(f"%{value}%"))
                else:
                    query = query.filter(column == value)
                    
    if default_order_by is not None:
        query = query.order_by(default_order_by)

    total = query.count()
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "items": items
    }
