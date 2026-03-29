import streamlit as st
from tutor import chat
import random
import re

UI = {
    "german": {
        "name": "Mathe-Miezi 🐾",
        "clear_chat": "Chatverlauf löschen",
        "chat_input": "Frag mich was zu Mathe...",
        "thinking": "Ich denke nach...",
        "language": "Deutsch",
        "avatar": "miezi.jpg",
        "send_files": "Abschicken 📨",
    },
    "italian": {
        "name": "Micio Matematico 🐾",
        "clear_chat": "Cancella la cronologia",
        "chat_input": "Chiedimi qualcosa di matematica...",
        "thinking": "Sto pensando...",
        "language": "Italiano",
        "avatar": "miezi.jpg",
        "send_files": "Invia 📨",
    },
}

GREETINGS = {
    "italian": [
        "Ciao! Sono qui per aiutarti con la matematica 🐾",
        "Benvenuta! Cosa studiamo oggi? 📐",
        "Ciao! Pronta per un po' di matematica? 🌟",
    ],
    "german": [
        "Hallo! Ich helfe dir gerne bei Mathe 🐾",
        "Willkommen! Was üben wir heute? 📐",
        "Hallo! Bereit für Mathematik? 🌟",
    ],
}

if "language" not in st.session_state:
    st.session_state.language = "italian"

if "messages" not in st.session_state:
    greeting = random.choice(GREETINGS[st.session_state.language])
    st.session_state.messages = [{"role": "assistant", "content": greeting}]

ui = UI[st.session_state.language]

st.set_page_config(page_title=ui["name"])
st.title(ui["name"])

# Sidebar
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
    greeting = random.choice(GREETINGS[st.session_state.language])
    st.session_state.messages = [{"role": "assistant", "content": greeting}]
    st.rerun()


def get_avatar(role: str) -> str | None:
    return ui["avatar"] if role == "assistant" else None


def render_text(text: str):
    text = re.sub(r"\\\[(.*?)\\\]", r"$$\1$$", text, flags=re.DOTALL)
    text = re.sub(r"\\\((.*?)\\\)", r"$\1$", text, flags=re.DOTALL)

    parts = re.split(r"(\$\$.*?\$\$)", text, flags=re.DOTALL)
    for part in parts:
        if part.startswith("$$") and part.endswith("$$"):
            st.latex(part[2:-2].strip())
        else:
            if part.strip():
                st.markdown(part)


def render_content(content):
    if isinstance(content, dict):
        if content.get("text"):
            render_text(content["text"])
        for file in content.get("files", []):
            if file.type in ("image/jpeg", "image/png"):
                st.image(file)
            elif file.type == "application/pdf":
                st.write(f"📄 {file.name}")
    else:
        render_text(content)


def handle_submission(text: str, files: list):
    user_content = {"text": text, "files": files}
    st.session_state.messages.append({"role": "user", "content": user_content})

    with st.chat_message("user"):
        render_content(user_content)

    with st.chat_message("assistant", avatar=get_avatar("assistant")):
        with st.spinner(ui["thinking"]):
            response = chat(
                messages=st.session_state.messages,
                language=ui["language"],
            )
        render_text(response)

    st.session_state.messages.append({"role": "assistant", "content": response})


# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=get_avatar(message["role"])):
        render_content(message["content"])

# Chat input
prompt = st.chat_input(
    ui["chat_input"],
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "pdf"],
)

if prompt and (prompt.text or prompt.files):
    handle_submission(text=prompt.text or "", files=prompt.files or [])
    st.rerun()
