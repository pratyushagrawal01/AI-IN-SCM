import streamlit as st
import os
import json

def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def initialize_session_state():
    if "chat" not in st.session_state:
        st.session_state.chat = []
    if "doc" not in st.session_state:
        st.session_state.doc = None
    if "chats" not in st.session_state:
        st.session_state.chats = {}
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = None
    if "pinned" not in st.session_state:
        st.session_state.pinned = set()
    if "rename_target" not in st.session_state:
        st.session_state.rename_target = None
    if "delete_target" not in st.session_state:
        st.session_state.delete_target = None
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False
    if "delete_pdf_index" not in st.session_state:
        st.session_state.delete_pdf_index = None

def save_chat(chat_name, chat_data):
    """Save chat data to disk."""
    chat_dir = os.path.join("chats", chat_name)
    os.makedirs(chat_dir, exist_ok=True)
    metadata_path = os.path.join(chat_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(chat_data, f, indent=4)

def load_chats():
    """Load all chats from disk into session state."""
    chats_dir = "chats"
    if os.path.exists(chats_dir):
        for chat_name in os.listdir(chats_dir):
            chat_dir = os.path.join(chats_dir, chat_name)
            if os.path.isdir(chat_dir):
                metadata_path = os.path.join(chat_dir, "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as f:
                        chat_data = json.load(f)
                    st.session_state.chats[chat_name] = chat_data
                    # Load pinned status if saved
                    if "pinned" in chat_data:
                        st.session_state.pinned.add(chat_name)

def delete_chat(chat_name):
    """Delete chat folder from disk."""
    chat_dir = os.path.join("chats", chat_name)
    if os.path.exists(chat_dir):
        import shutil
        shutil.rmtree(chat_dir)