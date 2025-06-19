from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ProductBase(BaseModel):
    product_name: str
    price_purchase: float
    price_sale: float
    quantity: int

class ProductCreate(ProductBase): pass
class ProductOut(ProductBase):
    product_id: int
    class Config:
        orm_mode = True

class SaleEntry(BaseModel):
    customer_name: str
    phone_no: str
    products: List[ProductCreate]
    bill_paid: bool
    payment_due_date: Optional[date]

class PurchaseEntry(BaseModel):
    vendor_name: str
    phone_no: str
    products: List[ProductCreate]
    bill_paid: bool
    payment_due_date: Optional[date]
