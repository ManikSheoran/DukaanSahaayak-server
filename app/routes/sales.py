from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, schemas, crud

router = APIRouter()

@router.post("/sales/")
def record_sale(sale: schemas.SaleEntry, db: Session = Depends(database.SessionLocal)):
    # Call a function in crud.py to process this sale
    return crud.handle_sale(db, sale)
