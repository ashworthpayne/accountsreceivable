from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Inventory, User
import schemas
from routers.auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/inventory/", response_model=list[schemas.InventorySchema])
def get_inventory(
    db: Session = Depends(get_db),
    search: str = None,
    min_price: float = None,
    max_price: float = None,
    low_stock: bool = False,
    sort_by: str = Query("item", regex="^(item|price|quantity_available)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)  # ✅ Require authentication
):
    """Retrieve inventory items with optional filters, sorting, and pagination."""
    
    query = db.query(Inventory)

    if search:
        query = query.filter(Inventory.item.contains(search))

    if min_price:
        query = query.filter(Inventory.price >= min_price)

    if max_price:
        query = query.filter(Inventory.price <= max_price)

    if low_stock:
        query = query.filter(Inventory.quantity_available < 10)  # Adjust threshold as needed

    # Sorting logic
    if order == "asc":
        query = query.order_by(getattr(Inventory, sort_by).asc())
    else:
        query = query.order_by(getattr(Inventory, sort_by).desc())

    inventory = query.offset(offset).limit(limit).all()

    return inventory

@router.post("/inventory/", response_model=schemas.InventorySchema)
def add_inventory_item(
    item: schemas.InventorySchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require authentication
):
    """Add a new inventory item (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    new_item = Inventory(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put("/inventory/{item}", response_model=schemas.InventorySchema)
def update_inventory_item(
    item: str,
    updated_item: schemas.InventorySchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require authentication
):
    """Update an inventory item (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    inventory = db.query(Inventory).filter(Inventory.item == item).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in updated_item.dict().items():
        setattr(inventory, key, value)

    db.commit()
    db.refresh(inventory)
    return inventory

@router.delete("/inventory/{item}", response_model=dict)
def delete_inventory_item(
    item: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require authentication
):
    """Delete an inventory item (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    inventory = db.query(Inventory).filter(Inventory.item == item).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(inventory)
    db.commit()
    return {"message": f"Item {item} deleted successfully"}
