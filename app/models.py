from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Date, Table
from sqlalchemy.orm import relationship
from .database import Base

class Customer(Base):
    __tablename__ = "customers"
    cust_id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    phone_no = Column(String)

class Vendor(Base):
    __tablename__ = "vendors"
    vend_id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String)
    phone_no = Column(String)

class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, unique=True)
    price_purchase = Column(Float)
    price_sale = Column(Float)
    quantity = Column(Integer)

class SalesData(Base):
    __tablename__ = "sales_data"
    sales_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.cust_id"))
    transaction_date = Column(Date)
    total_amount = Column(Float)
    total_quantity = Column(Integer)

class PurchaseData(Base):
    __tablename__ = "purchase_data"
    purch_id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vend_id"))
    transaction_date = Column(Date)
    total_amount = Column(Float)
    total_quantity = Column(Integer)

class ProfitLoss(Base):
    __tablename__ = "profit_loss"
    sales_id = Column(Integer, ForeignKey("sales_data.sales_id"), primary_key=True)
    is_profit = Column(Boolean)
    amount = Column(Float)

class SaleProduct(Base):
    __tablename__ = "sale_product"
    sales_id = Column(Integer, ForeignKey("sales_data.sales_id"), primary_key=True)
    prod_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)

class PurchaseProduct(Base):
    __tablename__ = "purchase_product"
    purch_id = Column(Integer, ForeignKey("purchase_data.purch_id"), primary_key=True)
    prod_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)

class UdharSales(Base):
    __tablename__ = "udhar_sales"
    udhar_id = Column(Integer, primary_key=True)
    sales_id = Column(Integer, ForeignKey("sales_data.sales_id"))
    date_of_entry = Column(Date)
    date_of_payment = Column(Date)

class UdharPurchase(Base):
    __tablename__ = "udhar_purchase"
    udhar_id = Column(Integer, primary_key=True)
    purch_id = Column(Integer, ForeignKey("purchase_data.purch_id"))
    date_of_entry = Column(Date)
    date_of_payment = Column(Date)
