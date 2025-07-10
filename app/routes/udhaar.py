from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from .. import database, models, schemas, utils
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

@router.post("/udhaar/sales/{id}/send_sms/")
def send_sales_udhaar_sms(
    id: int, db: Session = Depends(database.get_db)
):
    udhar = db.query(models.UdharSales).filter(models.UdharSales.udhar_id == id).first()
    if not udhar:
        raise HTTPException(status_code=404, detail="Udhar entry not found")

    sales = db.query(models.SalesData).filter(models.SalesData.sales_id == udhar.sales_id).first()
    if not sales:
        raise HTTPException(status_code=404, detail="Sales record not found")

    customer = db.query(models.Customer).filter(models.Customer.cust_id == sales.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    phone_no = customer.phone_no
    body = (
        f"Reminder: Sales udhaar due on {udhar.date_of_payment}.\n"
        f"Sales ID: {udhar.sales_id}\n"
        f"Entry Date: {udhar.date_of_entry}"
    )
    utils.send_sms(phone_no, body)

    return {"message": "SMS sent successfully", "phone": phone_no}

@router.post("/udhaar/purchases/{id}/send_sms/")
def send_purchase_udhaar_sms(
    id: int, db: Session = Depends(database.get_db)
):
    udhar = db.query(models.UdharPurchase).filter(models.UdharPurchase.udhar_id == id).first()
    if not udhar:
        raise HTTPException(status_code=404, detail="Udhar entry not found")

    purchase = db.query(models.PurchaseData).filter(models.PurchaseData.purch_id == udhar.purch_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase record not found")

    vendor = db.query(models.Vendor).filter(models.Vendor.vend_id == purchase.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
        
    body = (
        f"Reminder: Purchase udhaar due on {udhar.date_of_payment}.\n"
        f"Purchase ID: {udhar.purch_id}\n"
        f"Entry Date: {udhar.date_of_entry}"
    )
    utils.send_sms(vendor.phone_no, body)

    return {"message": "SMS sent successfully", "phone": vendor.phone_no}