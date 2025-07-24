from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from .database import Base, engine
from .routes import (
    inventory,
    sales,
    purchase,
    udhaar,
    profit_loss,
    customer,
    vendor,
    extract_products,
    chat
)

load_dotenv()

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(inventory.router, prefix="/api", tags=["Inventory"])
app.include_router(sales.router, prefix="/api", tags=["Sales"])
app.include_router(purchase.router, prefix="/api", tags=["Purchase"])
app.include_router(udhaar.router, prefix="/api", tags=["Udhaar"])
app.include_router(profit_loss.router, prefix="/api", tags=["ProfitLoss"])
app.include_router(customer.router, prefix="/api", tags=["Customer"])
app.include_router(vendor.router, prefix="/api", tags=["Vendor"])
app.include_router(extract_products.router, prefix="/api", tags=["ExtractProducts"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])

@app.get("/")
def root():
    return {"message": "Server is running."}

# Local run only
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
