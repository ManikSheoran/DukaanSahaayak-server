from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from .. import database, crud, models

router = APIRouter()

@router.get("/profit-loss/")
def get_profit_loss(db: Session = Depends(database.get_db)):
    return db.query(models.ProfitLoss).all()

@router.get("/profit-loss/{sales_id}")
def get_profit_loss_by_sale(sales_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.ProfitLoss).filter(models.ProfitLoss.sales_id == sales_id).all()

@router.get("/profit-loss/by-date/{query_date}")
def get_profit_loss_by_date(query_date: date, db: Session = Depends(database.get_db)):
    records = db.query(models.ProfitLoss).join(
        models.SalesData, models.ProfitLoss.sales_id == models.SalesData.sales_id
    ).filter(models.SalesData.transaction_date == query_date).all()
    return [record for record in records]
