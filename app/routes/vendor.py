from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, models, crud

router = APIRouter()


@router.get("/vendors/")
def get_vendors(db: Session = Depends(database.get_db)):
    return crud.get_all_vendors(db)


@router.get("/vendors/{vendor_id}")
def get_vendor_by_id(vendor_id: int, db: Session = Depends(database.get_db)):
    vendor = crud.get_vendor_by_id(db, vendor_id)
    if not vendor:
        return {"error": "Vendor not found"}
    return vendor
