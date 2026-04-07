from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.schemas.inventory import InventoryResponse, InventoryCreate, InventoryUpdate
from app.models.inventory import InventoryItem
from app.dependencies import get_current_user, require_role
import uuid

router = APIRouter()

@router.get("/", response_model=List[InventoryResponse])
async def get_inventory(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(select(InventoryItem))
    return result.scalars().all()

@router.get("/{id}", response_model=InventoryResponse)
async def get_item(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=InventoryResponse)
async def create_item(
    item_in: InventoryCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin", "staff"]))
):
    item = InventoryItem(**item_in.dict())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.put("/{id}", response_model=InventoryResponse)
async def update_item(
    id: uuid.UUID,
    item_in: InventoryUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin", "staff"]))
):
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item_in.dict(exclude_unset=True).items():
        setattr(item, key, value)
    
    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/{id}")
async def delete_item(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin"]))
):
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await db.delete(item)
    await db.commit()
    return {"status": "ok"}
