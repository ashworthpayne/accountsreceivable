from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.orm import Session, joinedload
from database import SessionLocal
from models import Invoice, User
import schemas
from auth import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime  # ✅ Fix missing import

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login/")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth dependency
def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid authentication")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ✅ Function to handle mixed date formats
def parse_inv_date(date_str):
    if isinstance(date_str, datetime):
        return date_str  # Already a datetime object, return as-is
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")  # Try ISO format
    except ValueError:
        return datetime.strptime(date_str, "%m/%d/%y")  # Fallback to short format

@router.get("/invoices/", response_model=dict)
def get_invoices(
    db: Session = Depends(get_db),
    custno: str = None,
    min_price: float = None,
    max_price: float = None,
    start_date: str = None,
    end_date: str = None,
    shipped: bool = None,
    sort_by: str = Query("inv_date", regex="^(inv_date|total_price|custno|shipped)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """Retrieve invoices with optional filters, sorting, and pagination."""
    query = db.query(Invoice).options(joinedload(Invoice.items))
    
    if custno:
        query = query.filter(Invoice.custno == custno)
    if min_price:
        query = query.filter(Invoice.total_price >= min_price)
    if max_price:
        query = query.filter(Invoice.total_price <= max_price)
    if start_date:
        query = query.filter(Invoice.inv_date >= start_date)
    if end_date:
        query = query.filter(Invoice.inv_date <= end_date)
    if shipped is not None:
        query = query.filter(Invoice.shipped == shipped)

    query = query.order_by(Invoice.inv_date.desc(), Invoice.invno.asc())  # ✅ Stable sorting for pagination

    total_count = query.count()
    invoices = query.offset(offset).limit(limit).all()
    
    return {
        "total": total_count,
        "invoices": [
            schemas.InvoiceSchema(
                invno=inv.invno,
                custno=inv.custno,
                total_price=inv.total_price,
                shipped=inv.shipped,
                inv_date=parse_inv_date(inv.inv_date)  # ✅ Handle mixed date formats
            ) for inv in invoices
        ]
    }

@router.put("/invoices/{invno}", response_model=schemas.InvoiceSchema)
def update_invoice(
    invno: str,
    updated_invoice: schemas.InvoiceSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an invoice (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    invoice = db.query(Invoice).filter(Invoice.invno == invno).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    for key, value in updated_invoice.dict().items():
        setattr(invoice, key, value)
    db.commit()
    db.refresh(invoice)
    return invoice

@router.delete("/invoices/{invno}", response_model=dict)
def delete_invoice(
    invno: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an invoice (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    invoice = db.query(Invoice).filter(Invoice.invno == invno).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.delete(invoice)
    db.commit()
    return {"message": f"Invoice {invno} deleted successfully"}

@router.put("/invoices/{invno}/ship", response_model=dict)
def mark_invoice_shipped(
    invno: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an invoice as shipped (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    invoice = db.query(Invoice).filter(Invoice.invno == invno).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice.shipped = True
    db.commit()
    db.refresh(invoice)
    return {"message": f"Invoice {invno} marked as shipped"}
