from fastapi import FastAPI
from .database import Base, engine
from .routes import inventory
from .routes import sales
from .routes import purchase
from .routes import udhaar
from .routes import profit_loss
from .routes import customer
from .routes import vendor
from .routes import extract_products
from .routes import chat
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*" ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)

app.include_router(inventory.router, prefix="/api", tags=["Inventory"])
app.include_router(sales.router, prefix="/api", tags=["Sales"])
app.include_router(purchase.router, prefix="/api", tags=["Purchase"])
app.include_router(udhaar.router, prefix="/api", tags=["Udhaar"])
app.include_router(profit_loss.router, prefix="/api", tags=["ProfitLoss"])
app.include_router(customer.router, prefix="/api", tags=["Customer"])
app.include_router(vendor.router, prefix="/api", tags=["Vendor"])
app.include_router(extract_products.router, prefix="/api", tags=["ExtractProducts"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
