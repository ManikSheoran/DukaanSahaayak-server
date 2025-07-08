from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models

router = APIRouter()

@router.get("/customers/{customer_id}")
def get_customer_by_id(customer_id: int, db: Session = Depends(database.get_db)):
    customer = db.query(models.Customer).filter(models.Customer.cust_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/customers")
def get_customer_by_phone(customer_phone_no: str, db: Session = Depends(database.get_db)):
    customer = db.query(models.Customer).filter(models.Customer.phone_no == customer_phone_no).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
