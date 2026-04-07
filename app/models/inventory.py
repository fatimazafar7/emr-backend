from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from app.database import Base

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clinic_id = Column(UUID(as_uuid=True), ForeignKey("clinics.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100))  # Medication, Supplies, Clinical
    stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=100)
    unit = Column(String(50))  # Capsules, Boxes, Vials, Pairs, Bags
    status = Column(String(50), default="In Stock")
    expiry_date = Column(DateTime(timezone=True))
    color = Column(String(50), default="indigo")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
