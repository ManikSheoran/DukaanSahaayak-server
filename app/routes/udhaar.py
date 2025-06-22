from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from .. import database, models, schemas

from datetime import timedelta

router = APIRouter()

# ------------------- GET SALES UDHAAR ----------------------
@router.get("/udhaar/sales/", response_model=list[schemas.UdharSalesOut])
def get_sales_udhaar(before: date = Query(None), db: Session = Depends(database.get_db)):
    query = db.query(models.UdharSales)
    if before:
        query = query.filter(models.UdharSales.date_of_payment <= before)
    return query.all()

# ------------------- GET PURCHASE UDHAAR -------------------
@router.get("/udhaar/purchases/", response_model=list[schemas.UdharPurchaseOut])
def get_purchase_udhaar(before: date = Query(None), db: Session = Depends(database.get_db)):
    query = db.query(models.UdharPurchase)
    if before:
        query = query.filter(models.UdharPurchase.date_of_payment <= before)
    return query.all()

# ------------------- DELETE SALES UDHAAR -------------------
@router.delete("/udhaar/sales/{udhar_id}")
def clear_sales_udhaar(udhar_id: int, db: Session = Depends(database.get_db)):
    udhar = db.query(models.UdharSales).filter(models.UdharSales.udhar_id == udhar_id).first()
    if not udhar:
        raise HTTPException(status_code=404, detail="Udhar entry not found")
    db.delete(udhar)
    db.commit()
    return {"msg": "Sales udhaar marked as paid and removed."}

# ------------------ DELETE PURCHASE UDHAAR ------------------
@router.delete("/udhaar/purchases/{udhar_id}")
def clear_purchase_udhaar(udhar_id: int, db: Session = Depends(database.get_db)):
    udhar = db.query(models.UdharPurchase).filter(models.UdharPurchase.udhar_id == udhar_id).first()
    if not udhar:
        raise HTTPException(status_code=404, detail="Udhar entry not found")
    db.delete(udhar)
    db.commit()
    return {"msg": "Purchase udhaar marked as paid and removed."}

@router.get("/udhaar/notifications/")
def get_due_udhaar_notifications(
    days_ahead: int = 3, db: Session = Depends(database.get_db)
):
    today = date.today()
    target = today + timedelta(days=days_ahead)

    sales_due = db.query(models.UdharSales).filter(
        models.UdharSales.date_of_payment <= target
    ).all()

    purchases_due = db.query(models.UdharPurchase).filter(
        models.UdharPurchase.date_of_payment <= target
    ).all()

    return {
        "days_ahead": days_ahead,
        "sales_udhaar_due": [
            {
                "udhar_id": u.udhar_id,
                "sales_id": u.sales_id,
                "due_date": u.date_of_payment,
                "entry_date": u.date_of_entry
            } for u in sales_due
        ],
        "purchase_udhaar_due": [
            {
                "udhar_id": u.udhar_id,
                "purch_id": u.purch_id,
                "due_date": u.date_of_payment,
                "entry_date": u.date_of_entry
            } for u in purchases_due
        ]
    }
