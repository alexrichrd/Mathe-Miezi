import streamlit as st
from tutor import chat

UI = {
    "german": {
        "name": "Mathe-Miezi 🐾",
        "greeting": "Wie kann ich dir heute helfen?",
        "clear_chat": "Chatverlauf löschen",
        "chat_input": "Frag mich was zu Mathe...",
        "thinking": "Ich denke nach...",
        "language": "Deutsch",
    },
    "italian": {
        "name": "Micio Matematico 🐾",
        "greeting": "Come posso aiutarti oggi?",
        "clear_chat": "Cancella la cronologia",
        "chat_input": "Chiedimi qualcosa di matematica...",
        "thinking": "Sto pensando...",
        "language": "Italiano",
    },
}

if "language" not in st.session_state:
    st.session_state.language = "italian"

ui = UI[st.session_state.language]

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": ui["greeting"]}]

st.set_page_config(page_title=ui["name"])
st.title(ui["name"])

st.sidebar.markdown("**Language / Lingua**")
de, it = st.sidebar.columns(2)
if de.button("🇩🇪 Deutsch", use_container_width=True):
    st.session_state.language = "german"
    st.rerun()
if it.button("🇮🇹 Italiano", use_container_width=True):
    st.session_state.language = "italian"
    st.rerun()

st.sidebar.divider()
if st.sidebar.button(ui["clear_chat"], use_container_width=True):
    st.session_state.messages = [{"role": "assistant", "content": ui["greeting"]}]
    st.rerun()

# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        if isinstance(content, dict):
            # Multimodal message: has text and/or files
            if content.get("text"):
                st.write(content["text"])
            for file in content.get("files", []):
                if file.type in ("image/jpeg", "image/png"):
                    st.image(file)
                elif file.type == "application/pdf":
                    st.write(f"📄 {file.name}")
        else:
            st.write(content)

# Chat input
prompt = st.chat_input(
    ui["chat_input"],
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "pdf"],
)

if prompt and (prompt.text or prompt.files):
    # Build structured message content
    user_content = {
        "text": prompt.text or "",
        "files": prompt.files or [],
    }

    # Append and display user message
    st.session_state.messages.append({"role": "user", "content": user_content})
    with st.chat_message("user"):
        if user_content["text"]:
            st.write(user_content["text"])
        for file in user_content["files"]:
            if file.type in ("image/jpeg", "image/png"):
                st.image(file)
            elif file.type == "application/pdf":
                st.write(f"📄 {file.name}")

    # Single call to chat() with full context
    with st.chat_message("assistant"):
        with st.spinner(ui["thinking"]):
            response = chat(
                messages=st.session_state.messages,
                language=ui["language"],
            )
        st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
