from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ✅ Company Schema
class CompanySchema(BaseModel):
    sysid: str
    company: str
    address: str

    class Config:
        orm_mode = True  # Ensures compatibility with SQLAlchemy

# ✅ System Settings Schema
class SystemSettingsSchema(BaseModel):
    sysid: str
    drive: str
    printer: str
    link: str

    class Config:
        orm_mode = True

# ✅ Financial Data Schema
class FinancialDataSchema(BaseModel):
    sysid: str
    num1: float
    num2: float
    num3: float
    num4: float
    num5: float

    class Config:
        orm_mode = True

class InventorySchema(BaseModel):
    item: str
    description: str
    quantity_available: float
    price: float

    class Config:
        orm_mode = True

class InvoiceItemSchema(BaseModel):
    item: str
    description: str
    qty_ordered: float
    qty_shipped: float
    price: float
    total_price: float
    inventory: Optional[InventorySchema] = None  # ✅ Include inventory details

    class Config:
        orm_mode = True

class InvoiceSchema(BaseModel):
    invno: str
    custno: str
    total_price: float
    shipped: bool
    inv_date: datetime

    class Config:
        from_attributes = True  # ✅ Correct for Pydantic v2

from pydantic import BaseModel

class CustomerSchema(BaseModel):
    id: int
    custno: str
    company: str
    address: str
    city: str
    state: str
    zip: str
    phone: str
    terms: str

    class Config:
        from_attributes = True  # ✅ Ensure ORM compatibility

# ✅ Schema for returning paginated customers
class PaginatedCustomers(BaseModel):
    total: int
    customers: List[CustomerSchema]
