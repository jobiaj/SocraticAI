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

load_dotenv()

app = FastAPI(title="Socrates AI")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

llm_service = LLMService()
nlp_processor = NLPProcessor()
socratic_dialogue = SocraticDialogue(llm_service, nlp_processor)

class DialogueRequest(BaseModel):
    message: str
    context: Optional[str] = None

class DialogueResponse(BaseModel):
    response: str
    processed_input: dict

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/dialogue")
async def create_dialogue(request: DialogueRequest):
    try:
        processed_input = nlp_processor.process(request.message)
        
        response = await socratic_dialogue.generate_response(
            request.message, 
            processed_input,
            request.context
        )
        
        return DialogueResponse(
            response=response,
            processed_input=processed_input
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dialogue", response_class=HTMLResponse)
async def dialogue_form(request: Request, message: str = Form(...)):
    try:
        processed_input = nlp_processor.process(message)
        response = await socratic_dialogue.generate_response(message, processed_input)
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "message": message,
            "response": response,
            "processed_input": processed_input
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": str(e)
        })

@app.get("/health")
async def health_check():
    return {"status": "healthy"}