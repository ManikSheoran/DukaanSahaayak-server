from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, crud

router = APIRouter()


@router.get("/vendors/")
def get_vendors(db: Session = Depends(database.get_db)):
    return crud.get_all_vendors(db)


@router.get("/vendors/{vendor_id}")
def get_vendor_by_id(vendor_id: int, db: Session = Depends(database.get_db)):
    vendor = db.query(models.Vendor).filter(models.Vendor.vend_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor
