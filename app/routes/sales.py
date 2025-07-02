from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, models, schemas, crud

router = APIRouter()

@router.post("/sales/")
def record_sale(sale: schemas.SaleEntry, db: Session = Depends(database.get_db)):
    return crud.handle_sale(db, sale)


@router.get("/sales/")
def get_sales(db: Session = Depends(database.get_db)):
    return crud.get_all_sales(db)

@router.get("/sales/{sale_id}")
def get_sale_by_id(sale_id: int, db: Session = Depends(database.get_db)):
    sale = crud.get_sale_by_id(db, sale_id)
    if not sale:
        return {"error": "Sale not found"}
    return sale
