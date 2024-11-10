import os
import subprocess
from threading import Thread
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import torch
import streamlit as st
import requests

# Set environment variable to disable Hugging Face symlink warning
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

# Define the Streamlit UI as a function
def run_streamlit():
    st.title("Radiate AI Mental Health Chatbot")
    st.write("Welcome! Type a message below to chat with our AI support bot.")

    # Backend API endpoint URL - This URL will need to be the same as the FastAPI endpoint
    API_URL = "http://localhost:8000/chat"  # Modify if using an external URL

    # Initialize session state for storing chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # User input field
    user_message = st.text_input("You:")

    if user_message:
        try:
            # Send message to backend and get the AI response
            response = requests.post(API_URL, json={"message": user_message})
            ai_response = response.json().get("response", "Sorry, I didn’t understand that.")
        except requests.exceptions.RequestException:
            ai_response = "Error: Could not connect to the server."

        # Update chat history
        st.session_state["chat_history"].append(("You", user_message))
        st.session_state["chat_history"].append(("AI", ai_response))

        # Clear the input field
        user_message = ""

    # Display chat history
    for speaker, message in st.session_state["chat_history"]:
        st.write(f"{speaker}: {message}")

# Run Streamlit in a separate thread
def start_streamlit():
    # Start Streamlit as a subprocess
    subprocess.run(["streamlit", "run", __file__])

# Start the Streamlit thread
Thread(target=start_streamlit, daemon=True).start()

# Run the FastAPI application if this is the main file
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

