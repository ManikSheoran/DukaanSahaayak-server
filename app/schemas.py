from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ProductEntry(BaseModel):
    product_name: str
    quantity: int
    rate: float
    sale_price: Optional[float] = None

class ProductBase(BaseModel):
    product_name: str
    price_purchase: float
    price_sale: float
    quantity: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    price_purchase: Optional[float] = None
    price_sale: Optional[float] = None
    quantity: Optional[int] = None

class ProductOut(ProductBase):
    product_id: int
    class Config:
        orm_mode = True

class SaleEntry(BaseModel):
    customer_name: str
    phone_no: str
    products: List[ProductEntry]
    bill_paid: bool
    payment_due_date: Optional[date] = None

class PurchaseEntry(BaseModel):
    vendor_name: str
    phone_no: str
    products: List[ProductEntry]
    bill_paid: bool
    payment_due_date: Optional[date] = None

class UdharSalesOut(BaseModel):
    udhar_id: int
    sales_id: int
    date_of_entry: date
    date_of_payment: date

    class Config:
        orm_mode = True

class UdharPurchaseOut(BaseModel):
    udhar_id: int
    purch_id: int
    date_of_entry: date
    date_of_payment: date

    class Config:
        orm_mode = True