from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class InventoryBase(BaseModel):
    name: str
    category: Optional[str] = "Clinical"
    stock: int = 0
    min_stock: int = 100
    unit: Optional[str] = "Units"
    status: Optional[str] = "In Stock"
    expiry_date: Optional[datetime] = None
    color: Optional[str] = "indigo"
    clinic_id: UUID

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    stock: Optional[int] = None
    min_stock: Optional[int] = None
    unit: Optional[str] = None
    status: Optional[str] = None
    expiry_date: Optional[datetime] = None
    color: Optional[str] = None

class InventoryResponse(InventoryBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
