import streamlit as st
import json
import os
from langchain_client import GroqClient

# ─── CONFIG ───────────────────────────────────────────────
st.set_page_config(page_title="AI Code Assistant", page_icon="💻", layout="wide")

CHAT_DB = "chats.json"

# ─── LOAD ALL CHATS ───────────────────────────────────────
def load_all_chats():
    if os.path.exists(CHAT_DB):
        with open(CHAT_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ─── SAVE ALL CHATS ───────────────────────────────────────
def save_all_chats(data):
    with open(CHAT_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ─── INIT STATE ────────────────────────────────────────────
if "chats" not in st.session_state:
    st.session_state.chats = load_all_chats()

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Chat"

# create default chat if empty
if st.session_state.current_chat not in st.session_state.chats:
    st.session_state.chats[st.session_state.current_chat] = []

# ─── UI TITLE ──────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center;'>💻 AI Code Assistant</h1>",
    unsafe_allow_html=True
)

# ─── SIDEBAR (CHAT LIST LIKE CHATGPT) ─────────────────────
st.sidebar.title("💬 Chats")

# New Chat Button
if st.sidebar.button("➕ New Chat"):
    new_name = f"Chat {len(st.session_state.chats)+1}"
    st.session_state.chats[new_name] = []
    st.session_state.current_chat = new_name
    save_all_chats(st.session_state.chats)
    st.rerun()

# Chat selector (ChatGPT style list)
chat_names = list(st.session_state.chats.keys())
selected_chat = st.sidebar.radio("Your Chats", chat_names)

st.session_state.current_chat = selected_chat
messages = st.session_state.chats[selected_chat]

st.sidebar.markdown("---")

# Clear current chat
if st.sidebar.button("🗑️ Clear This Chat"):
    st.session_state.chats[selected_chat] = []
    save_all_chats(st.session_state.chats)
    st.rerun()

# ─── SETTINGS ──────────────────────────────────────────────
mode = st.sidebar.selectbox("Mode", [
    "General Chat",
    "Code Generator",
    "Debugger",
    "Optimizer",
])

model_name = st.sidebar.selectbox("Model", [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
])

# ─── MODE INFO ─────────────────────────────────────────────
st.info({
    "General Chat": "Chat with AI",
    "Code Generator": "Generate code",
    "Debugger": "Fix code issues",
    "Optimizer": "Optimize code"
}[mode])

# ─── SHOW CHAT MESSAGES ───────────────────────────────────
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── INPUT ────────────────────────────────────────────────
user_input = st.chat_input("Message AI Assistant...")

if user_input:

    # user msg
    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                client = GroqClient(model_name=model_name, mode=mode)
                reply = client.chat(messages)

                st.markdown(reply)
                messages.append({"role": "assistant", "content": reply})

            except Exception as e:
                st.error(f"Error: {e}")

    # SAVE EVERYTHING (IMPORTANT)
    st.session_state.chats[selected_chat] = messages
    save_all_chats(st.session_state.chats)