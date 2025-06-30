from fastapi import FastAPI
from .database import Base, engine
from .routes import inventory
from .routes import sales
from .routes import purchase
from .routes import udhaar
from fastapi.middleware.cors import CORSMiddleware

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
