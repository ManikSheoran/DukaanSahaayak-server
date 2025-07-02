from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, schemas, crud

router = APIRouter()

@router.post("/purchases/")
def record_purchase(purchase: schemas.PurchaseEntry, db: Session = Depends(database.get_db)):
    return crud.handle_purchase(db, purchase)


@router.get("/purchases/")
def get_purchases(db: Session = Depends(database.get_db)):
    return crud.get_all_purchases(db)

@router.get("/purchases/{purchase_id}")
def get_purchase_by_id(purchase_id: int, db: Session = Depends(database.get_db)):
    purchase = crud.get_purchase_by_id(db, purchase_id)
    if not purchase:
        return {"error": "Purchase not found"}
    return purchase
