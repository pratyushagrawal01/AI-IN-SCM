import streamlit as st
import os
from AI_Module import run_query
from Text_Extraction import extract_and_save
from Table_Extraction import extract_tables
from Comparison_Table import generate_comparison_table
from ui_utils import save_chat
import pandas as pd
import re

def render_main_area():
    # TOP ANCHOR
    st.markdown("<div id='top'></div>", unsafe_allow_html=True)
    
    # TITLE
    st.title("📄 Document Clause Chatbot")
    if st.session_state.current_chat:
        st.subheader(f"💬 Active Chat: {st.session_state.current_chat}")
    else:
        st.subheader("Select or create a chat to get started!")
    
    # DOCUMENT SELECTION
    if st.session_state.doc is None:
        with st.expander("📤 Upload PDFs for This Chat", expanded=True):
            uploaded_files = st.file_uploader("Upload PDFs (e.g., RFP and Quotations)", type="pdf", accept_multiple_files=True, help="Upload one or more PDFs to analyze in this chat")
            if uploaded_files:
                pdf_types = []
                for i, uploaded in enumerate(uploaded_files):
                    pdf_type = st.selectbox(f"Type for {uploaded.name}", ["Quotation", "RFP"], index=0 if i > 0 else 1, key=f"type_{i}")
                    pdf_types.append(pdf_type)
                
                rfp_count = pdf_types.count("RFP")
                if rfp_count > 1:
                    st.error("Only one PDF can be marked as RFP. Please adjust and try again.")
                elif rfp_count == 0:
                    st.warning("No RFP selected. Defaulting the first PDF to RFP.")
                    pdf_types[0] = "RFP"
                
                if st.button("Confirm Upload", key="confirm_upload"):
                    chat_name = f"Chat_{len(st.session_state.chats) + 1}"
                    chat_dir = os.path.join("chats", chat_name)
                    os.makedirs(chat_dir, exist_ok=True)
                    
                    st.session_state.all_docs = []
                    st.session_state.all_pdfs = []
                    st.session_state.all_pdf_names = []
                    for i, uploaded in enumerate(uploaded_files):
                        filename = f"doc_{i+1}.pdf"
                        pdf_path = os.path.join(chat_dir, filename)
                        with open(pdf_path, "wb") as f:
                            f.write(uploaded.getbuffer())
                        extract_and_save(pdf_path)  # This will create txt in chat_dir
                        st.session_state.all_docs.append(os.path.join(chat_dir, f"doc_{i+1}_extracted.txt"))
                        st.session_state.all_pdfs.append(pdf_path)
                        st.session_state.all_pdf_names.append(uploaded.name)
                    
                    rfp_index = pdf_types.index("RFP")
                    st.session_state.all_docs.insert(0, st.session_state.all_docs.pop(rfp_index))
                    st.session_state.all_pdfs.insert(0, st.session_state.all_pdfs.pop(rfp_index))
                    st.session_state.all_pdf_names.insert(0, st.session_state.all_pdf_names.pop(rfp_index))
                    
                    st.success(f"{len(uploaded_files)} PDF(s) uploaded and extracted!")
                    
                    st.session_state.current_chat = chat_name
                    st.session_state.doc = st.session_state.all_docs[0]
                    st.session_state.current_pdf = st.session_state.all_pdfs[0]
                    st.session_state.chat = []
                    st.session_state.chats[chat_name] = {
                        "file": st.session_state.doc,
                        "pdf": st.session_state.current_pdf,
                        "all_docs": st.session_state.all_docs,
                        "all_pdfs": st.session_state.all_pdfs,
                        "all_pdf_names": st.session_state.all_pdf_names,
                        "messages": [],
                        "tables": [],
                        "comparison_table": None,
                        "pinned": False
                    }
                    save_chat(chat_name, st.session_state.chats[chat_name])
                    st.rerun()
        st.stop()
    
    # SCM COMPARISON TABLE DISPLAY
    st.markdown('<div id="fixed-comparison">', unsafe_allow_html=True)
    current_comparison = st.session_state.chats.get(st.session_state.current_chat, {}).get("comparison_table", None)
    with st.expander("📊 SCM Comparison table", expanded=bool(current_comparison)):
        if current_comparison is not None:
            st.dataframe(current_comparison, width="stretch", height=300)
            if st.button("🗑️ Clear Comparison Table", help="Remove the comparison table for this chat"):
                st.session_state.chats[st.session_state.current_chat]["comparison_table"] = None
                save_chat(st.session_state.current_chat, st.session_state.chats[st.session_state.current_chat])
                st.rerun()
        else:
            st.info("No comparison table generated yet. Use the sidebar to generate one.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CHAT DISPLAY
    st.markdown("---")
    st.subheader("💬 Chat Messages")
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    if st.session_state.chat:
        for msg in st.session_state.chat:
            box_class = "chat-user" if msg["role"] == "user" else "chat-bot"
            st.markdown(
                f"""
                <div class="{box_class}">
                    <strong>{msg['role'].title()}:</strong><br>
                    {msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No messages yet. Ask a question below!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CHAT INPUT WITH CLIP BUTTON
    st.markdown("---")
    col1, col2 = st.columns([12, 1.2])
    with col1:
        query = st.chat_input("Type your query and press Enter")
    with col2:
        if st.button("➕", help="Add more PDFs to this chat"):
            st.session_state.show_uploader = True
    
    # Mid-Chat PDF Adder
    if st.session_state.show_uploader:
        additional_files = st.file_uploader("", type="pdf", accept_multiple_files=True, key="additional")
        if additional_files:
            chat_dir = os.path.join("chats", st.session_state.current_chat)
            start_index = len(st.session_state.chats[st.session_state.current_chat]["all_pdfs"])
            for i, uploaded in enumerate(additional_files):
                filename = f"doc_{start_index + i + 1}.pdf"
                pdf_path = os.path.join(chat_dir, filename)
                with open(pdf_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                extract_and_save(pdf_path)
                st.session_state.chats[st.session_state.current_chat]["all_docs"].append(os.path.join(chat_dir, f"doc_{start_index + i + 1}_extracted.txt"))
                st.session_state.chats[st.session_state.current_chat]["all_pdfs"].append(pdf_path)
                st.session_state.chats[st.session_state.current_chat]["all_pdf_names"].append(uploaded.name)
            save_chat(st.session_state.current_chat, st.session_state.chats[st.session_state.current_chat])
            st.success(f"Added {len(additional_files)} more PDF(s) to the chat.")
            st.session_state.show_uploader = False
            st.rerun()
    
    # Send Query
    if query:
        answer = run_query(
            st.session_state.doc, 
            query, 
            st.session_state.current_pdf, 
            st.session_state.chats[st.session_state.current_chat].get("all_docs"), 
            st.session_state.chats[st.session_state.current_chat].get("all_pdfs"),
            st.session_state.chats[st.session_state.current_chat].get("all_pdf_names")
        )
        highlighted = re.sub(
            f"({re.escape(query)})",
            r"<span class='highlight'>\1</span>",
            answer,
            flags=re.IGNORECASE
        )
        highlighted = highlighted.replace("\n", "<br>")
        
        st.session_state.chat.append({"role": "user", "content": query})
        st.session_state.chat.append({"role": "assistant", "content": highlighted})
        st.session_state.chats[st.session_state.current_chat]["messages"] = st.session_state.chat
        save_chat(st.session_state.current_chat, st.session_state.chats[st.session_state.current_chat])
        st.rerun()
    
    # BOTTOM ANCHOR
    st.markdown("<div id='bottom'></div>", unsafe_allow_html=True)
    
    # FLOATING SCROLL BUTTONS
    st.markdown("""
    <a href="#top">
        <button class="float-btn" id="topBtn" title="Scroll to top">⬆</button>
    </a>
    <a href="#bottom">
        <button class="float-btn" id="botBtn" title="Scroll to bottom">⬇</button>
    </a>
    """, unsafe_allow_html=True)