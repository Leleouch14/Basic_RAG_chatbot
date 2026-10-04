import streamlit as st
import uuid
from api import upload_document, ask_backend, fetch_all_chats, sync_chat_state, purge_chat

st.set_page_config(page_title="Study Assistant", page_icon="📖", layout="wide")

# -----------------------------------------------------------------------------
# STATE INITIALIZATION (Pulling from SQLite via API)
# -----------------------------------------------------------------------------
if "chats" not in st.session_state:
    db_data = fetch_all_chats()
    st.session_state.chats = {cid: data["messages"] for cid, data in db_data.items()}
    st.session_state.chat_names = {cid: data["chat_name"] for cid, data in db_data.items()}

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None

def create_new_session():
    new_id = uuid.uuid4().hex
    session_number = len(st.session_state.chats) + 1
    new_name = f"Session {session_number}"
    
    st.session_state.chats[new_id] = []
    st.session_state.chat_names[new_id] = new_name
    st.session_state.active_chat_id = new_id
    sync_chat_state(new_id, new_name, [])

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("📚 Study Vaults")
    
    if st.button("➕ New Chat", use_container_width=True):
        create_new_session()
        st.rerun()
    
    st.divider()

    st.caption("Your Chats")
    for chat_id, chat_name in st.session_state.chat_names.items():
        button_label = f"👉 {chat_name}" if chat_id == st.session_state.active_chat_id else chat_name
        if st.button(button_label, key=f"session_{chat_id}", use_container_width=True):
            st.session_state.active_chat_id = chat_id
            st.rerun()

    if st.session_state.active_chat_id:
        st.divider()
        st.subheader("Add Study Material")
        
        uploaded_file = st.file_uploader("Select PDF or Code/MD file", label_visibility="collapsed")
        if uploaded_file is not None:
            if st.button("Ingest Document", use_container_width=True):
                with st.spinner("Chunking & embedding..."):
                    result = upload_document(uploaded_file, st.session_state.active_chat_id)
                    if result["success"]:
                        st.success(f"Ingested {result['data'].get('chunks', 0)} chunks!")
                    else:
                        st.error(f"Upload failed: {result['error']}")
        
        st.divider()
        # DELETION LOGIC
        if st.button("🗑️ Delete Current Chat", type="primary", use_container_width=True):
            purge_chat(st.session_state.active_chat_id)
            del st.session_state.chats[st.session_state.active_chat_id]
            del st.session_state.chat_names[st.session_state.active_chat_id]
            st.session_state.active_chat_id = None
            st.rerun()

# -----------------------------------------------------------------------------
# MAIN SCREEN
# -----------------------------------------------------------------------------
if not st.session_state.active_chat_id:
    st.header("Welcome to Study Assistant")
    st.write("Click **➕ New Chat** to begin.")
else:
    current_chat_id = st.session_state.active_chat_id
    current_chat_name = st.session_state.chat_names[current_chat_id]
    
    st.header(f"💬 {current_chat_name}")

    for message in st.session_state.chats[current_chat_id]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("grounded"):
                st.success("✅ Grounded in uploaded materials", icon="✅")
                if message.get("sources"):
                    st.markdown("**Citations:**")
                    for source in message["sources"]:
                        st.caption(f"- 📄 {source['file']} (Page {source['page']})")
            elif message["role"] == "assistant" and not message.get("grounded"):
                st.warning("⚠️ No relevant information found in your files. Answer bypassed.", icon="⚠️")

    user_input = st.chat_input("Ask a question about your files...")
    
    if user_input:
        st.session_state.chats[current_chat_id].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing context..."):
                response = ask_backend(user_input, current_chat_id)
                
                if response["success"]:
                    data = response["data"]
                    answer = data.get("answer", "No answer returned.")
                    sources = data.get("sources", [])
                    grounded = data.get("grounded", False)
                    
                    st.markdown(answer)
                    
                    if grounded:
                        st.success("✅ Grounded in uploaded materials", icon="✅")
                        if sources:
                            st.markdown("**Citations:**")
                            for source in sources:
                                st.caption(f"- 📄 {source['file']} (Page {source['page']})")
                    else:
                        st.warning("⚠️ No relevant information found in your files. Answer bypassed.", icon="⚠️️")
                    
                    st.session_state.chats[current_chat_id].append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "grounded": grounded
                    })
                    
                    # Persist state to SQLite after full interaction
                    sync_chat_state(current_chat_id, current_chat_name, st.session_state.chats[current_chat_id])
                else:
                    st.error(f"Network Error: {response['error']}")