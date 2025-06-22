from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, schemas, crud

router = APIRouter()

@router.post("/sales/")
def record_sale(sale: schemas.SaleEntry, db: Session = Depends(database.get_db)):
    return crud.handle_sale(db, sale)
