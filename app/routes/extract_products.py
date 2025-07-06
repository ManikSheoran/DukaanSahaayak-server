from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from .. import crud, database
import google.generativeai as genai
from rapidfuzz import process, fuzz
import os
import base64
import re
import json

router = APIRouter()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.0-flash")

def get_inventory_names(db: Session):
    inventory = crud.get_all_products(db)
    return [p.product_name for p in inventory]

def match_product(name: str, inventory: list[str], threshold: int = 70):
    match, score, _ = process.extractOne(name, inventory, scorer=fuzz.ratio)
    print(inventory, match, name, score)
    return match if score >= threshold else None

@router.post("/extract-products")
async def extract_products(
    image: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    contents = await image.read()
    base64_image = base64.b64encode(contents).decode("utf-8")

    try:
        response = model.generate_content([
            {
                "inline_data": {
                    "mime_type": image.content_type,
                    "data": base64_image,
                }
            },
            "Extract product names and quantities in JSON format. Format: [{\"product_name\": string, \"quantity\": number}]"
        ])

        text = response.text.strip()

        match = re.search(r"```(json)?\s*([\s\S]*?)\s*```", text)
        if match:
            json_text = match.group(2)
        else:
            json_text = text

        extracted = json.loads(json_text)
        inventory_names = get_inventory_names(db)

        matched_products = []
        print("Extracted JSON:", extracted)
        for item in extracted:
            name = item.get("product_name", "")
            qty = item.get("quantity", 0)
            matched_name = match_product(name, inventory_names)
            if matched_name:
                matched_products.append({
                    "product_name": matched_name,
                    "quantity": qty,
                })

            print("Matched Products:", matched_products)

        return {"products": matched_products}

    except Exception as e:
        return {"error": str(e)}
