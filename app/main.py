from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from app.llm_service import LLMService
from app.nlp_processor import NLPProcessor
from app.socratic_dialogue import SocraticDialogue
from app.ml_categorizer import PhilosophicalCategorizer

load_dotenv()

app = FastAPI(title="Socrates AI")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

llm_service = LLMService()
nlp_processor = NLPProcessor()
categorizer = PhilosophicalCategorizer()

# Try to load the pre-trained model
try:
    if not categorizer.load_model():
        print("Warning: ML model not found. Training new model...")
        categorizer.train()
except Exception as e:
    print(f"Warning: Could not load ML categorizer: {e}")
    categorizer = None

socratic_dialogue = SocraticDialogue(llm_service, nlp_processor)

class DialogueRequest(BaseModel):
    message: str
    context: Optional[str] = None

class DialogueResponse(BaseModel):
    response: str
    processed_input: dict
    category: Optional[str] = None
    category_description: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/dialogue")
async def create_dialogue(request: DialogueRequest):
    try:
        processed_input = nlp_processor.process(request.message)
        
        # Categorize the input if categorizer is available
        category = None
        category_description = None
        if categorizer:
            try:
                category, _ = categorizer.predict(request.message)
                category_description = categorizer.get_category_description(category)
            except Exception as e:
                print(f"Categorization failed: {e}")
        
        response = await socratic_dialogue.generate_response(
            request.message, 
            processed_input,
            request.context,
            category,
            category_description
        )
        
        return DialogueResponse(
            response=response,
            processed_input=processed_input,
            category=category,
            category_description=category_description
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dialogue", response_class=HTMLResponse)
async def dialogue_form(request: Request, message: str = Form(...)):
    try:
        processed_input = nlp_processor.process(message)
        
        # Categorize the input if categorizer is available
        category = None
        category_description = None
        if categorizer:
            try:
                category, _ = categorizer.predict(message)
                category_description = categorizer.get_category_description(category)
            except Exception as e:
                print(f"Categorization failed: {e}")
        
        response = await socratic_dialogue.generate_response(
            message, 
            processed_input,
            None,
            category,
            category_description
        )
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "message": message,
            "response": response,
            "processed_input": processed_input,
            "category": category,
            "category_description": category_description
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": str(e)
        })

@app.get("/health")
async def health_check():
    return {"status": "healthy"}