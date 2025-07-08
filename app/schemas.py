from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


# For sales, use a separate schema matching your required fields
class SaleProductEntry(BaseModel):
    product_name: str
    quantity: float
    rate: float
    sale_price: float
    total_amount: float

class ProductEntry(BaseModel):
    product_name: str
    quantity: float
    price_purchase: float
    price_sale: float

class ProductBase(BaseModel):
    product_name: str
    price_purchase: float
    price_sale: float
    quantity: float

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    price_purchase: Optional[float] = None
    price_sale: Optional[float] = None
    quantity: Optional[float] = None

class ProductOut(ProductBase):
    product_id: int
    class Config:
        orm_mode = True

class SaleEntry(BaseModel):
    customer_name: str
    phone_no: str
    products: List[SaleProductEntry]
    transaction_date: date = Field(default_factory=date.today)
    bill_paid: bool
    payment_due_date: Optional[date] = None
    total_amount: float

class PurchaseEntry(BaseModel):
    vendor_name: str
    phone_no: str
    products: List[ProductEntry]
    transaction_date: date = Field(default_factory=date.today)
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