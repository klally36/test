import streamlit as st
from transformers import pipeline
from textblob import TextBlob
import re

# Initialize NLP Models
@st.cache_resource
def load_models():
    chatbot = pipeline("conversational", model="microsoft/DialoGPT-medium")
    sentiment_analyzer = pipeline("sentiment-analysis")
    return chatbot, sentiment_analyzer

chatbot, sentiment_analyzer = load_models()

# Set up the Streamlit app
st.set_page_config(page_title="Mental Health Chatbot", page_icon="💬", layout="centered")
st.title("💬 Mental Health Chatbot")
st.markdown("""
Welcome! I'm here to listen and provide support. Remember, I'm not a substitute for professional help, but I can offer resources and a listening ear.
""")

# Initialize session state for conversation history and feedback
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "feedback" not in st.session_state:
    st.session_state.feedback = []

# Function to generate chatbot response
def get_chatbot_response(user_input):
    # Analyze sentiment
    sentiment = sentiment_analyzer(user_input)[0]
    sentiment_label = sentiment['label']
    sentiment_score = sentiment['score']

    # Generate response
    response = chatbot(user_input)[0]['generated_text']
    
    # Tailor response based on sentiment
    if sentiment_label == "NEGATIVE":
        response += " I'm really sorry you're feeling this way. It might help to talk to a trusted person or a mental health professional."
    elif sentiment_label == "POSITIVE":
        response += " That's great to hear! Keep taking care of yourself."
    else:
        response += " I'm here to support you. Feel free to share more about how you're feeling."

    return response

# Function to sanitize user input
def sanitize_input(user_input):
    # Remove any unwanted characters or scripts
    sanitized = re.sub(r'[^\w\s]', '', user_input)
    return sanitized

# User input
user_input = st.text_input("You:", key="input")

# Send button
if st.button("Send"):
    if user_input.strip() != "":
        sanitized_input = sanitize_input(user_input)
        # Add user message to conversation
        st.session_state.conversation.append({"sender": "You", "message": sanitized_input})
        # Get bot response
        bot_response = get_chatbot_response(sanitized_input)
        st.session_state.conversation.append({"sender": "Bot", "message": bot_response})
        # Scroll to bottom
        st.experimental_rerun()

# Display conversation
st.markdown("### Conversation")
for chat in st.session_state.conversation:
    if chat["sender"] == "You":
        st.markdown(f"**You:** {chat['message']}")
    else:
        st.markdown(f"**Bot:** {chat['message']}")

# Feedback Section
st.markdown("### Provide Feedback")
feedback = st.radio("How helpful was this response?", ("", "⭐️", "⭐️⭐️", "⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️"))
if st.button("Submit Feedback"):
    if feedback:
        st.session_state.feedback.append(feedback)
        st.success("Thank you for your feedback!")
        # Optionally, reset feedback selection
        st.session_state["feedback"] = ""
    else:
        st.warning("Please select a feedback option.")

# Resources Section
st.markdown("### Helpful Resources")
st.markdown("""
- [National Suicide Prevention Lifeline](https://suicidepreventionlifeline.org/) - 1-800-273-TALK (8255)
- [Crisis Text Line](https://www.crisistextline.org/) - Text HOME to 741741
- [Mental Health America](https://www.mhanational.org/) - Resources and support
- [Mind](https://www.mind.org.uk/) - Mental health information and support
""")

# Privacy Notice
st.markdown("""
---
**Privacy Notice:** This chatbot does not store any personal information. Conversations are not saved and are intended for support purposes only. If you are in crisis, please reach out to a mental health professional or a trusted individual.
""")

