from fastapi import FastAPI, Depends
from .database import Base, engine
from .routes import sales  # import your routes
from sqlalchemy.orm import Session
from app.database import get_db

app = FastAPI()

# Create all tables
Base.metadata.create_all(bind=engine)

# Include your routers
app.include_router(sales.router, prefix="/api/sales", tags=["Sales"])
@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    return {"msg": "Connected to PostgreSQL"}
