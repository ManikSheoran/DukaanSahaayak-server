from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, schemas, crud

router = APIRouter()

@router.post("/purchases/")
def record_purchase(purchase: schemas.PurchaseEntry, db: Session = Depends(database.get_db)):
    return crud.handle_purchase(db, purchase)
