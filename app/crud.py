from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date

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
    customer = db.query(models.Customer).filter_by(customer_name=name, phone_no=phone).first()
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

    for p in sale.products:
        product = get_product_by_name(db, p.product_name)
        if not product:
            product = models.Product(
                product_name=p.product_name,
                price_purchase=p.rate,
                price_sale=p.sale_price if p.sale_price is not None else p.rate,
                quantity=0 
            )
            db.add(product)
            db.commit()
            db.refresh(product)
        if product.quantity < p.quantity:
            # Allow negative inventory if you want to record the sale anyway
            # Or, you can set product.quantity = 0 and allow negative stock
            product.quantity -= p.quantity
        else:
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

    sale_entry.total_amount = total_amt
    sale_entry.total_quantity = total_qty
    db.commit()

    if not sale.bill_paid:
        db.add(models.UdharSales(
            sales_id=sale_entry.sales_id,
            date_of_entry=sale.transaction_date,
            date_of_payment=sale.payment_due_date
        ))
        db.commit()

    return {"msg": "Sale recorded", "sale_id": sale_entry.sales_id}

def get_or_create_vendor(db: Session, name: str, phone: str):
    vendor = db.query(models.Vendor).filter_by(vendor_name=name, phone_no=phone).first()
    if not vendor:
        vendor = models.Vendor(vendor_name=name, phone_no=phone)
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
    return vendor

def handle_purchase(db: Session, purchase: schemas.PurchaseEntry):
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

    for p in purchase.products:
        product = get_or_create_product(db, p)
        product.price_purchase = p.rate
        if p.sale_price is not None:
            product.price_sale = p.sale_price
        product.quantity += p.quantity
        db.commit()

        link = models.PurchaseProduct(purch_id=purch_entry.purch_id, prod_id=product.product_id)
        db.add(link)

        total_amt += p.quantity * p.rate
        total_qty += p.quantity

    purch_entry.total_amount = total_amt
    purch_entry.total_quantity = total_qty
    db.commit()

    if not purchase.bill_paid:
        db.add(models.UdharPurchase(
            purch_id=purch_entry.purch_id,
            date_of_entry=purchase.transaction_date,
            date_of_payment=purchase.payment_due_date
        ))
        db.commit()

    return {"msg": "Purchase recorded", "purchase_id": purch_entry.purch_id}
