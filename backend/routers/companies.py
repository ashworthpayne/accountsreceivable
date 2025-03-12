from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Company  # ✅ Import directly
from schemas import CompanySchema  # ✅ Import directly

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/companies/", response_model=list[CompanySchema])
def get_companies(
    db: Session = Depends(get_db),
    name: str = None,  # ✅ Optional filter by name
    limit: int = 10,    # ✅ Pagination limit
    offset: int = 0     # ✅ Pagination offset
):
    """Retrieve companies with optional filters and pagination"""
    query = db.query(Company)
    
    if name:
        query = query.filter(Company.name.ilike(f"%{name}%"))  # ✅ Case-insensitive name search

    total_count = query.count()
    companies = query.offset(offset).limit(limit).all()

    return companies


@router.get("/companies/{sysid}", response_model=CompanySchema)  # ✅ Fixed
def get_company(sysid: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.sysid == sysid).first()  # ✅ Fixed
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.post("/companies/", response_model=CompanySchema)  # ✅ Fixed
def create_company(company: CompanySchema, db: Session = Depends(get_db)):  # ✅ Fixed
    new_company = Company(**company.dict())  # ✅ Fixed
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return new_company

@router.put("/companies/{sysid}", response_model=CompanySchema)
def update_company(sysid: str, company_update: CompanySchema, db: Session = Depends(get_db)):
    """Update an existing company"""
    company = db.query(Company).filter(Company.sysid == sysid).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    for key, value in company_update.dict().items():
        setattr(company, key, value)

    db.commit()
    db.refresh(company)
    return company


@router.delete("/companies/{sysid}", response_model=dict)
def delete_company(sysid: str, db: Session = Depends(get_db)):
    """Delete a company"""
    company = db.query(Company).filter(Company.sysid == sysid).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    db.delete(company)
    db.commit()
    return {"message": f"Company {sysid} deleted successfully"}
