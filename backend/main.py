from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from parse_user_input import parse_user_input
from rank_hotels import rank_hotels
import json
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import re

# comment
def clean_json_string(json_str):
    """Remove ```json and ``` wrappers from LLM responses."""
    return re.sub(r"^```json\s*|\s*```$", "", json_str.strip(), flags=re.MULTILINE)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static/dist", html=True), name="static")

@app.get("/")
def serve_spa():
    return FileResponse(os.path.join("static/dist", "index.html"))

class Query(BaseModel):
    message: str

@app.post("/recommend")
def recommend_hotels(query: Query):
    try:
        print("📝 User query received:", query.message)
        
        filters = parse_user_input(query.message)
        cleaned_filters = clean_json_string(filters)
        filters_dict = json.loads(cleaned_filters)

        top_hotels = rank_hotels(filters_dict, query.message)
        return top_hotels  # <- ✅ Already a list of dicts!

    except ValueError as ve:
        print("🚫 User message was irrelevant.")
        return {"error": str(ve)}

    except Exception as e:
        print("❌ Unexpected error:", e)
        return {"error": str(e)}