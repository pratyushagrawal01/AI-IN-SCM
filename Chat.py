import streamlit as st
from ui_utils import load_css, initialize_session_state, load_chats
from sidebar_components import render_sidebar
from main_area_components import render_main_area

# -------------------------------
# PAGE CONFIG
# -------------------------------

st.set_page_config(
    page_title="Document Clause Chatbot",
    layout="wide",
    page_icon="📄"
)

# -------------------------------
# INITIALIZE
# -------------------------------

initialize_session_state()
load_css()
load_chats()  # Load persistent chats

# -------------------------------
# RENDER COMPONENTS
# -------------------------------

render_sidebar()
render_main_area()