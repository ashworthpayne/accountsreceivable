from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    sysid = Column(String, unique=True, index=True)
    company = Column(String)
    address = Column(String)

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    sysid = Column(String, unique=True, index=True)
    drive = Column(String)
    printer = Column(String)
    link = Column(String)

class FinancialData(Base):
    __tablename__ = "financial_data"

    id = Column(Integer, primary_key=True, index=True)
    sysid = Column(String, unique=True, index=True)
    num1 = Column(Float)
    num2 = Column(Float)
    num3 = Column(Float)
    num4 = Column(Float)
    num5 = Column(Float)

class Inventory(Base):  # ✅ Correct place for SQLAlchemy models
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    item = Column(String, unique=True, index=True)
    description = Column(String)
    quantity_available = Column(Float)
    price = Column(Float)

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invno = Column(String, unique=True, index=True)
    custno = Column(String, index=True)
    inv_date = Column(String)
    po_number = Column(String)
    total_price = Column(Float)
    shipped = Column(Boolean, default=False)  # ✅ Ensure "shipped" column is in "invoices"

    items = relationship("InvoiceItem", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invno = Column(String, ForeignKey("invoices.invno"))
    item = Column(String, ForeignKey("inventory.item"))
    description = Column(String)
    qty_ordered = Column(Float)
    qty_shipped = Column(Float)
    price = Column(Float)
    total_price = Column(Float)

    invoice = relationship("Invoice", back_populates="items")
    inventory = relationship("Inventory")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")  # ✅ Default role is "user"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    custno = Column(String, unique=True, nullable=False)
    company = Column(String, nullable=False)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    terms = Column(String, nullable=True)