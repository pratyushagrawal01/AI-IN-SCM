

import os


import streamlit as st
from AI_Module import run_query
from Text_Extraction import extract_and_save
from Table_Extraction import extract_tables
from Comparison_Table import generate_comparison_table
from ui_utils import save_chat, delete_chat
import pandas as pd

def render_sidebar():
    st.sidebar.title("📂 Chat History")
    
    chat_names = list(st.session_state.chats.keys())
    pinned_chats = [c for c in chat_names if c in st.session_state.pinned]
    normal_chats = [c for c in chat_names if c not in st.session_state.pinned]
    ordered_chats = pinned_chats + normal_chats
    
    if ordered_chats:
        for name in ordered_chats:
            cols = st.sidebar.columns([2, 0.005, 1, 1], gap="xsmall")
            
            # OPEN CHAT
            with cols[0]:
                label =  f"{name}"
                is_active = name == st.session_state.current_chat
                display_label = f"**_{label}_**" if is_active else label
                if st.button(display_label, key=f"open_{name}", help=f"Open chat: {name}"):
                    chat_data = st.session_state.chats[name]
                    backend_folder = chat_data.get("backend_key", name.strip())
                    st.session_state.chat = chat_data.get("messages", [])
                    st.session_state.doc = chat_data["file"]
                    st.session_state.current_pdf = chat_data.get("pdf", name + ".pdf")
                    st.session_state.current_chat = backend_folder
                    # Fix: Ensure doc path exists for reload
                    if not os.path.exists(st.session_state.doc):
                        chat_dir = os.path.join("chats", backend_folder)
                        st.session_state.doc = os.path.join(chat_dir, "doc_1_extracted.txt")
                    st.session_state.current_display_name = name

                    # Initialize missing keys
                    if "tables" not in st.session_state.chats[name]:
                        st.session_state.chats[name]["tables"] = []
                    if "pdf" not in st.session_state.chats[name]:
                        st.session_state.chats[name]["pdf"] = name + ".pdf"
                    if "all_docs" not in st.session_state.chats[name]:
                        st.session_state.chats[name]["all_docs"] = [st.session_state.chats[name]["file"]]
                    if "all_pdfs" not in st.session_state.chats[name]:
                        st.session_state.chats[name]["all_pdfs"] = [st.session_state.chats[name]["pdf"]]
                    if "all_pdf_names" not in st.session_state.chats[name]:
                        st.session_state.chats[name]["all_pdf_names"] = [os.path.basename(st.session_state.chats[name]["pdf"])]
                    st.rerun()
            
           
            # RENAME
            with cols[2]:
                if st.button("✏️", key=f"rename_{name}", help="Rename this chat"):
                    st.session_state.rename_target = name
            
            # DELETE
            with cols[3]:
                if st.button("🗑️", key=f"delete_{name}", help="Delete this chat"):
                    st.session_state.delete_target = name
    else:
        st.sidebar.info("No chats yet. Create a new one below!")
    
    # RENAME CHAT
    if st.session_state.rename_target:
        with st.sidebar.expander("✏️ Rename Chat", expanded=True):
            new_name = st.text_input("New name", value=st.session_state.rename_target, help="Enter a new name for the chat").strip()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save", key="save_rename"):
                    old = st.session_state.rename_target
                    if new_name and new_name not in st.session_state.chats:
                        st.session_state.chats[new_name] = st.session_state.chats.pop(old)
                        if old in st.session_state.pinned:
                            st.session_state.pinned.remove(old)
                            st.session_state.pinned.add(new_name)
                        # Rename folder
                        old_dir = os.path.join("chats", old)
                        new_dir = os.path.join("chats", new_name)
                        if os.path.exists(old_dir):
                            os.rename(old_dir, new_dir)
                        save_chat(new_name, st.session_state.chats[new_name])
                        if st.session_state.current_chat == old:
                            st.session_state.current_chat = new_name
                        st.session_state.rename_target = None
                        st.rerun()
                with col2:
                    if st.button("Cancel", key="cancel_rename"):
                        st.session_state.rename_target = None
                        st.rerun()
    
    # DELETE CHAT
    if st.session_state.delete_target:
        with st.sidebar.expander("⚠️ Delete Chat", expanded=True):
            st.write(f"Are you sure you want to delete **{st.session_state.delete_target}**? This action cannot be undone.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Cancel", key="cancel_delete"):
                    st.session_state.delete_target = None
                    st.rerun()
            with col2:
                if st.button("Delete", key="confirm_delete"):
                    name = st.session_state.delete_target
                    delete_chat(name)  # Delete from disk
                    del st.session_state.chats[name]
                    if name in st.session_state.pinned:
                        st.session_state.pinned.remove(name)
                    if st.session_state.current_chat == name:
                        st.session_state.current_chat = None
                        st.session_state.chat = []
                        st.session_state.doc = None
                    st.session_state.delete_target = None
                    st.rerun()
    
    # NEW CHAT
    st.sidebar.markdown("---")
    if st.sidebar.button("➕ New Chat", use_container_width=True, help="Start a new chat"):
        st.session_state.chat = []
        st.session_state.doc = None
        st.session_state.current_chat = None
        st.session_state.show_uploader = False
        st.rerun()
    
    # PDFs IN THIS CHAT
    st.sidebar.markdown("---")
    with st.sidebar.expander("📄 PDFs in This Chat", expanded=False):
        current_pdf_names = st.session_state.chats.get(st.session_state.current_chat, {}).get("all_pdf_names", [])
        if current_pdf_names:
            for i, pdf_name in enumerate(current_pdf_names):
                cols = st.columns([3, 1])
                source = "RFP" if i == 0 else f"Quotation {i}"
                with cols[0]:
                    st.write(f"- {source}: {pdf_name}")
                with cols[1]:
                    if st.button("🗑️", key=f"delete_pdf_{i}", help=f"Delete {pdf_name} from this chat"):
                        st.session_state.delete_pdf_index = i
                        st.rerun()
            
            # Confirmation
            if st.session_state.delete_pdf_index is not None:
                pdf_to_delete = current_pdf_names[st.session_state.delete_pdf_index]
                st.markdown("---")
                st.write(f"Confirm delete: **{pdf_to_delete}**?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Cancel", key="cancel_delete_pdf"):
                        st.session_state.delete_pdf_index = None
                        st.rerun()
                with col2:
                    if st.button("Delete", key="confirm_delete_pdf"):
                        # Delete from disk
                        chat_dir = os.path.join("chats", st.session_state.current_chat)
                        pdf_path = os.path.join(chat_dir, st.session_state.chats[st.session_state.current_chat]["all_pdfs"][st.session_state.delete_pdf_index])
                        txt_path = pdf_path.replace('.pdf', '_extracted.txt')
                        if os.path.exists(pdf_path):
                            os.remove(pdf_path)
                        if os.path.exists(txt_path):
                            os.remove(txt_path)
                        # Remove from lists
                        del st.session_state.chats[st.session_state.current_chat]["all_docs"][st.session_state.delete_pdf_index]
                        del st.session_state.chats[st.session_state.current_chat]["all_pdfs"][st.session_state.delete_pdf_index]
                        del st.session_state.chats[st.session_state.current_chat]["all_pdf_names"][st.session_state.delete_pdf_index]
                        if st.session_state.chats[st.session_state.current_chat]["all_docs"]:
                            st.session_state.doc = st.session_state.chats[st.session_state.current_chat]["all_docs"][0]
                            st.session_state.current_pdf = st.session_state.chats[st.session_state.current_chat]["all_pdfs"][0]
                        else:
                            st.session_state.doc = None
                            st.session_state.current_pdf = None
                        save_chat(st.session_state.current_chat, st.session_state.chats[st.session_state.current_chat])
                        st.session_state.delete_pdf_index = None
                        st.success(f"Deleted {pdf_to_delete} from the chat.")
                        st.rerun()
        else:
            st.write("No PDFs in this chat yet.")
    
    # SCM TOOLS
    st.sidebar.markdown("---")
    with st.sidebar.expander("🔧 SCM Tools", expanded=False):
        if st.button("Give SCM Comparison table", key="comparison_btn", help="Generate a comparison table of key parameters from RFP and Quotations"):
            if st.session_state.current_chat:
                comparison_table = generate_comparison_table(
                    st.session_state.chats[st.session_state.current_chat].get("all_docs"),
                    st.session_state.chats[st.session_state.current_chat].get("all_pdfs"),
                    st.session_state.chats[st.session_state.current_chat].get("all_pdf_names")
                )
                if comparison_table is not None:
                    st.session_state.chats[st.session_state.current_chat]["comparison_table"] = comparison_table
                    save_chat(st.session_state.current_chat, st.session_state.chats[st.session_state.current_chat])
                    st.success("SCM Comparison table generated! View it in the main area.")
                else:
                    st.warning("No data found for comparison.")
            else:
                st.info("Select a chat first to generate the comparison table.")