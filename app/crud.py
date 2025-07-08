from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def send_sms(to_number: str, body: str):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not account_sid or not auth_token:
        print("Twilio credentials not set")
        return
    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            body=body,
            from_="+15413258526",
            to="+919728084306"
        )
        print(f"SMS sent to {to_number}: {message.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_all_products(db: Session):
    return db.query(models.Product).all()

def get_product_by_name(db: Session, name: str):
    return db.query(models.Product).filter_by(product_name=name).first()

def update_product(db: Session, product_id: int, updates: schemas.ProductUpdate):
    db_product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not db_product:
        return None
    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product

def get_or_create_customer(db: Session, name: str, phone: str):
    customer = db.query(models.Customer).filter(models.Customer.phone_no == phone).first()
    if not customer:
        customer = models.Customer(customer_name=name, phone_no=phone)
        db.add(customer)
        db.commit()
        db.refresh(customer)
    return customer

def get_or_create_product(db: Session, product: schemas.ProductEntry):
    prod = db.query(models.Product).filter_by(product_name=product.product_name).first()
    if not prod:
        prod = models.Product(
            product_name=product.product_name,
            price_purchase=product.rate,
            price_sale=product.sale_price if product.sale_price is not None else product.rate * 1.1,
            quantity=0
        )
        db.add(prod)
        db.commit()
        db.refresh(prod)
    return prod

def handle_sale(db: Session, sale: schemas.SaleEntry):
    if not sale.phone_no:
        sale.phone_no = 9999999999
    customer = get_or_create_customer(db, sale.customer_name, sale.phone_no)
    total_amt, total_qty = 0, 0

    sale_entry = models.SalesData(
        customer_id=customer.cust_id,
        transaction_date=sale.transaction_date,
        total_amount=0,
        total_quantity=0
    )
    db.add(sale_entry)
    db.commit()
    db.refresh(sale_entry)

    bill_lines = []
    for p in sale.products:
        product = get_product_by_name(db, p.product_name)
        if not product:
            raise Exception(f"Product '{p.product_name}' does not exist in inventory. Please add it to inventory first.")
        product.quantity -= p.quantity
        db.commit()
        link = models.SaleProduct(sales_id=sale_entry.sales_id, prod_id=product.product_id)
        db.add(link)
        total_amt += p.quantity * p.rate
        total_qty += p.quantity
        profit = (p.rate - product.price_purchase) * p.quantity
        db.add(models.ProfitLoss(
            sales_id=sale_entry.sales_id,
            is_profit=profit >= 0,
            amount=abs(profit)
        ))
        # Add product line to bill
        bill_lines.append(f"{p.product_name}: {p.quantity} x {p.rate} = {p.total_amount}")

    sale_entry.total_amount = total_amt
    sale_entry.total_quantity = total_qty
    db.commit()

    # Send SMS if phone_no exists
    if sale.phone_no:
        bill_status = "PAID" if sale.bill_paid else f"DUE by {sale.payment_due_date}"
        bill_text = (
            f"Bill for {sale.customer_name}\n"
            f"Date: {sale.transaction_date}\n"
            f"----------------------\n"
            + "\n".join(bill_lines) +
            f"\n----------------------\n"
            f"Total: {total_amt}\n"
            f"Status: {bill_status}"
        )
        send_sms(sale.phone_no, bill_text)

    if not sale.bill_paid:
        db.add(models.UdharSales(
            sales_id=sale_entry.sales_id,
            date_of_entry=sale.transaction_date,
            date_of_payment=sale.payment_due_date
        ))
        db.commit()

    return {"msg": "Sale recorded", "sale_id": sale_entry.sales_id}

def get_or_create_vendor(db: Session, name: str, phone: str):
    vendor = db.query(models.Vendor).filter_by(phone_no=phone).first()
    if not vendor:
        vendor = models.Vendor(vendor_name=name, phone_no=phone)
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
    return vendor

def handle_purchase(db: Session, purchase: schemas.PurchaseEntry):
    if not purchase.phone_no:
        purchase.phone_no = 9999999999
    vendor = get_or_create_vendor(db, purchase.vendor_name, purchase.phone_no)
    total_amt, total_qty = 0, 0

    purch_entry = models.PurchaseData(
        vendor_id=vendor.vend_id,
        transaction_date=purchase.transaction_date,
        total_amount=0,
        total_quantity=0
    )
    db.add(purch_entry)
    db.commit()
    db.refresh(purch_entry)

    bill_lines = []
    for p in purchase.products:
        product = get_product_by_name(db, p.product_name)
        if not product:
            product = models.Product(
                product_name=p.product_name,
                price_purchase=p.price_purchase,
                price_sale=p.price_sale,
                quantity=p.quantity
            )
            db.add(product)
            db.commit()
            db.refresh(product)
        else:
            old_qty = product.quantity
            new_qty = p.quantity
            total_qty_update = old_qty + new_qty
            if total_qty_update > 0:
                product.price_purchase = (
                    (product.price_purchase * old_qty + p.price_purchase * new_qty) / total_qty_update
                )
            product.price_sale = p.price_sale
            product.quantity = total_qty_update
            db.commit()
        link = models.PurchaseProduct(purch_id=purch_entry.purch_id, prod_id=product.product_id)
        db.add(link)
        total_amt += p.quantity * p.price_purchase
        total_qty += p.quantity
        
        bill_lines.append(f"{p.product_name}: {p.quantity} x {p.price_purchase} = {p.quantity * p.price_purchase}")

    purch_entry.total_amount = total_amt
    purch_entry.total_quantity = total_qty
    db.commit()

    if purchase.phone_no:
        bill_status = "PAID" if purchase.bill_paid else f"DUE by {purchase.payment_due_date}"
        bill_text = (
            f"Purchase Bill for {purchase.vendor_name}\n"
            f"Date: {purchase.transaction_date}\n"
            f"----------------------\n"
            + "\n".join(bill_lines) +
            f"\n----------------------\n"
            f"Total: {total_amt}\n"
            f"Status: {bill_status}"
        )
        send_sms(purchase.phone_no, bill_text)

    if not purchase.bill_paid:
        db.add(models.UdharPurchase(
            purch_id=purch_entry.purch_id,
            date_of_entry=purchase.transaction_date,
            date_of_payment=purchase.payment_due_date
        ))
        db.commit()

    return {"msg": "Purchase recorded", "purchase_id": purch_entry.purch_id}

def get_all_sales(db: Session):
    return db.query(models.SalesData).all()

def get_all_purchases(db: Session):
    return db.query(models.PurchaseData).all()

def get_all_vendors(db: Session):
    return db.query(models.Vendor).all()

def get_sale_by_id(db: Session, sale_id: int):
    return db.query(models.SalesData).filter(models.SalesData.sales_id == sale_id).first()

def get_purchase_by_id(db: Session, purchase_id: int):
    return db.query(models.PurchaseData).filter(models.PurchaseData.purch_id == purchase_id).first()

def get_vendor_by_id(db: Session, vendor_id: int):
    return db.query(models.Vendor).filter(models.Vendor.vend_id == vendor_id).first()
