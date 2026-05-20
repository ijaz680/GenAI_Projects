import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.title("🤖 Groq Chatbot")

# Sidebar - Model selector
st.sidebar.title("⚙️ Settings")
model_name = st.sidebar.selectbox("Choose Free Model", [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-8b-8192",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
    "deepseek-r1-distill-llama-70b",
])

# Clear chat button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Initialize chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):

    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY not found in .env file.")
        st.stop()

    # Show user message
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get Groq response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                client = Groq(api_key=GROQ_API_KEY)

                response = client.chat.completions.create(
                    model=model_name,
                    messages=st.session_state.messages,
                )

                reply = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.write(reply)

            except Exception as e:
                st.error(f"Error: {e}")