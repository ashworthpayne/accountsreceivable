from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Customer  # ✅ Import Customer model
import schemas
from auth import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login/")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Authentication dependency
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
    return username  # ✅ Returning username for now

@router.get("/customers/", response_model=schemas.PaginatedCustomers)
def get_customers(
    db: Session = Depends(get_db),
    company: str = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieve customers with optional filtering and pagination."""
    query = db.query(Customer)

    if company:
        query = query.filter(Customer.company.ilike(f"%{company}%"))

    total_count = query.count()
    customers = query.offset(offset).limit(limit).all()

    print(f"📌 Fetching customers with limit={limit}, offset={offset}, total_count={total_count}")  # ✅ Debugging

    return {"total": total_count, "customers": customers}


# ✅ Get a single customer by custno
@router.get("/customers/{custno}", response_model=schemas.CustomerSchema)
def get_customer(custno: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.custno == custno).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# ✅ Create a new customer
@router.post("/customers/", response_model=schemas.CustomerSchema)
def create_customer(customer: schemas.CustomerSchema, db: Session = Depends(get_db)):
    existing_customer = db.query(Customer).filter(Customer.custno == customer.custno).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer number already exists")
    new_customer = Customer(**customer.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

# ✅ Update an existing customer
@router.put("/customers/{custno}", response_model=schemas.CustomerSchema)
def update_customer(custno: str, customer_update: schemas.CustomerSchema, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.custno == custno).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    for key, value in customer_update.dict().items():
        setattr(customer, key, value)
    
    db.commit()
    db.refresh(customer)
    return customer

# ✅ Delete a customer
@router.delete("/customers/{custno}", response_model=dict)
def delete_customer(custno: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.custno == custno).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    return {"message": f"Customer {custno} deleted successfully"}
