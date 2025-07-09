from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter()

@router.post("/products/", response_model=schemas.ProductOut)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    product_name = product.product_name.strip().capitalize()
    db_product = crud.get_product_by_name(db, product_name)
    if db_product:
        raise HTTPException(status_code=400, detail="Product already exists")
    product_data = schemas.ProductCreate(
        product_name=product_name,
        price_purchase=product.price_purchase,
        price_sale=product.price_sale,
        quantity=product.quantity
    )
    return crud.create_product(db, product_data)

@router.get("/products/", response_model=list[schemas.ProductOut])
def list_products(db: Session = Depends(database.get_db)):
    return crud.get_all_products(db)

@router.put("/products/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, updates: schemas.ProductUpdate, db: Session = Depends(database.get_db)):
    updated = crud.update_product(db, product_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(database.get_db)):
    deleted = crud.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"msg": "Product deleted successfully"}

@router.put("/products/{product_name}")
def update_product_quantity(product_name: str, quantity: float = Body(..., embed=True), db: Session = Depends(database.get_db)):
    product_name_cap = product_name.strip().capitalize()
    product = crud.get_product_by_name(db, product_name_cap)
    if not product:
        product = crud.create_product(db, schemas.ProductCreate(
            product_name=product_name_cap,
            price_purchase=0, 
            price_sale=0,
            quantity=quantity
        ))
        return {"msg": "Product created", "product_name": product.product_name, "quantity": product.quantity}
    else:
        product.quantity = product.quantity + quantity
        db.commit()
        db.refresh(product)
        return {"msg": "Quantity updated", "product_name": product.product_name, "quantity": product.quantity}
