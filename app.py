import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import torch

# Suppress symlink warning for Hugging Face
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Initialize FastAPI app
app = FastAPI()

# Enable CORS to allow frontend to access this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the text-generation pipeline for conversational responses
conversation_pipeline = pipeline("text-generation", model="microsoft/DialoGPT-medium")

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    response = conversation_pipeline(user_message, max_length=50, num_return_sequences=1)
    ai_response = response[0]["generated_text"]
    return {"response": ai_response}
