from fastapi import FastAPI
from .database import Base, engine
from .routes import sales  # import your routes

app = FastAPI()

# Create all tables
Base.metadata.create_all(bind=engine)

# Include your routers
app.include_router(sales.router, prefix="/api/sales", tags=["Sales"])
