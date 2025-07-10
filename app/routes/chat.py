from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from .. import database
import google.generativeai as genai
import os
import re

router = APIRouter()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.0-flash")

def extract_sql_query(text: str) -> str:
    match = re.search(r"SELECT .*?;", text, re.IGNORECASE | re.DOTALL)
    return match.group(0) if match else None

def contains_unsafe_sql(query: str) -> bool:
    unsafe_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "MERGE", "REPLACE", "EXEC", "CALL"]
    return any(re.search(rf"\b{kw}\b", query, re.IGNORECASE) for kw in unsafe_keywords)

@router.post("/ai/sql")
def get_ai_answer(prompt: str, db: Session = Depends(database.get_db)):
    query = None
    data = []
    try:
        system_prompt = (
            "You are a SQL assistant. Given a question, respond with a syntactically correct "
            "PostgreSQL SELECT query. The database contains the following tables:\n"
            "- customers(cust_id, customer_name, phone_no)\n"
            "- vendors(vend_id, vendor_name, phone_no)\n"
            "- products(product_id, product_name, price_purchase, price_sale, quantity)\n"
            "- sales_data(sales_id, customer_id, transaction_date, total_amount, total_quantity)\n"
            "- purchase_data(purch_id, vendor_id, transaction_date, total_amount, total_quantity)\n"
            "- profit_loss(id, sales_id, is_profit, amount)\n"
            "- udhar_sales(udhar_id, sales_id, date_of_entry, date_of_payment)\n"
            "- udhar_purchase(udhar_id, purch_id, date_of_entry, date_of_payment)\n"
            "Use only SELECT queries. Assume all dates are in YYYY-MM-DD format."
            "Do not include explanations, only return the query."
        )

        response = model.generate_content([system_prompt, prompt])
        generated_text = response.text.strip()

        query = extract_sql_query(generated_text)
        if not query:
            return {
                "answer": "I'm sorry, I couldn't understand your request well enough to form a database query. Please try rephrasing.",
                "error": "Could not generate a valid SQL query from the prompt.",
                "generated_text": generated_text,
                "query": None,
                "columns": [],
                "data": data,
            }

        if contains_unsafe_sql(query):
            return {
                "answer": "For security reasons, I can only perform read-only queries. Please ask a question that doesn't require changing data.",
                "error": "Unsafe SQL operation detected. Only SELECT queries are allowed.",
                "query": query,
                "columns": [],
                "data": data,
            }

        result = db.execute(text(query))
        columns = list(result.keys())
        rows = result.fetchall()
        data = [dict(zip(columns, row)) for row in rows]

        if not rows:
            answer_prompt = (
                f"The user asked: '{prompt}'. A database query was run but returned no results. "
                "Politely inform the user that you couldn't find any data for their request."
            )
        else:
            limited_rows = rows[:20]
            data_for_prompt = f"Columns: {', '.join(columns)}\n"
            for row in limited_rows:
                data_for_prompt += f"Row: {', '.join(map(str, row))}\n"
            if len(rows) > 20:
                data_for_prompt += f"\n... and {len(rows) - 20} more rows."

            answer_prompt = (
                "You are a helpful assistant. Based on the user's question and the following data from the database, "
                "provide a clear and concise answer in natural language. Do not mention that you are looking at data or SQL. "
                "Just give the answer as if you already knew it."
                f"\n\nUser's Question: \"{prompt}\""
                f"\n\nData:\n{data_for_prompt}"
            )

        answer_response = model.generate_content(answer_prompt)
        final_answer = answer_response.text.strip()

        return {
            "answer": final_answer,
            "query": query,
            "columns": columns,
            "data": data,
            "error": None,
        }
    except Exception as e:
        return {
            "answer": "I'm sorry, I encountered an error while trying to answer your question.",
            "error": f"An error occurred: {str(e)}",
            "query": query,
            "columns": [],
            "data": data,
        }