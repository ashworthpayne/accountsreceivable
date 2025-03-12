from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/financial-data/", response_model=list[schemas.FinancialDataSchema])
def get_all_financial_data(db: Session = Depends(get_db)):
    return db.query(models.FinancialData).all()

@router.get("/financial-data/{sysid}", response_model=schemas.FinancialDataSchema)
def get_financial_record(sysid: str, db: Session = Depends(get_db)):
    record = db.query(models.FinancialData).filter(models.FinancialData.sysid == sysid).first()
    if not record:
        raise HTTPException(status_code=404, detail="Financial record not found")
    return record

@router.put("/financial-data/{sysid}", response_model=schemas.FinancialDataSchema)
def update_financial_record(sysid: str, updated_record: schemas.FinancialDataSchema, db: Session = Depends(get_db)):
    record = db.query(models.FinancialData).filter(models.FinancialData.sysid == sysid).first()
    if not record:
        raise HTTPException(status_code=404, detail="Financial record not found")

    for key, value in updated_record.dict().items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record
