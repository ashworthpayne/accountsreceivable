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

@router.get("/system-settings/", response_model=list[schemas.SystemSettingsSchema])
def get_all_settings(db: Session = Depends(get_db)):
    return db.query(models.SystemSettings).all()

@router.get("/system-settings/{sysid}", response_model=schemas.SystemSettingsSchema)
def get_setting(sysid: str, db: Session = Depends(get_db)):
    setting = db.query(models.SystemSettings).filter(models.SystemSettings.sysid == sysid).first()
    if not setting:
        raise HTTPException(status_code=404, detail="System setting not found")
    return setting

@router.put("/system-settings/{sysid}", response_model=schemas.SystemSettingsSchema)
def update_setting(sysid: str, updated_setting: schemas.SystemSettingsSchema, db: Session = Depends(get_db)):
    setting = db.query(models.SystemSettings).filter(models.SystemSettings.sysid == sysid).first()
    if not setting:
        raise HTTPException(status_code=404, detail="System setting not found")

    for key, value in updated_setting.dict().items():
        setattr(setting, key, value)

    db.commit()
    db.refresh(setting)
    return setting
