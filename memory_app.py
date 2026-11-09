import uuid
import sqlite3
from pathlib import Path
import requests
import streamlit as st
from langchain_classic.chains import ConversationChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_ollama import OllamaLLM
st.set_page_config(
    page_title="MemoSphere AI | Memory Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "memosphere.db"
DEFAULT_MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://localhost:11434"
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
def create_conversation():
    chat_id = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO conversations (id, title) VALUES (?, ?)",
            (chat_id, "New conversation")
        )
    return chat_id
def get_conversations():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, title, updated_at
            FROM conversations
            ORDER BY updated_at DESC
        """).fetchall()
    return [dict(row) for row in rows]
def get_messages(chat_id):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
        """, (chat_id,)).fetchall()
    return [dict(row) for row in rows]
def save_conversation(chat_id, prompt, answer):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
        """, (chat_id, "user", prompt))
        conn.execute("""
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
        """, (chat_id, "assistant", answer))
        row = conn.execute(
            "SELECT title FROM conversations WHERE id = ?",
            (chat_id,)
        ).fetchone()
        if row and row["title"] == "New conversation":
            title = prompt.strip().replace("\n", " ")
            title = title[:40] + ("..." if len(title) > 40 else "")
            conn.execute(
                "UPDATE conversations SET title = ? WHERE id = ?",
                (title or "New conversation", chat_id)
            )
        conn.execute("""
            UPDATE conversations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (chat_id,))
def clear_conversation(chat_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM messages WHERE conversation_id = ?",
            (chat_id,)
        )
        conn.execute("""
            UPDATE conversations
            SET title = 'New conversation',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (chat_id,))
init_db()
@st.cache_resource
def load_llm():
    return OllamaLLM(
        model=DEFAULT_MODEL,
        base_url=OLLAMA_URL,
        temperature=0.7
    )
def ollama_is_running():
    try:
        response = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=3
        )
        return response.ok
    except requests.RequestException:
        return False

def load_memory(chat_id):
    memory = ConversationBufferMemory(
        memory_key="history",
        input_key="input",
        return_messages=False
    )
    for message in get_messages(chat_id):
        if message["role"] == "user":
            memory.chat_memory.add_user_message(
                message["content"]
            )
        elif message["role"] == "assistant":
            memory.chat_memory.add_ai_message(
                message["content"]
            )
    return memory
def ask_memosphere(prompt):
    llm = load_llm()
    chain = ConversationChain(
        llm=llm,
        memory=st.session_state.memory,
        verbose=False
    )
    return chain.predict(input=prompt)
if "chat_id" not in st.session_state:
    st.session_state.chat_id = create_conversation()
if "memory" not in st.session_state:
    st.session_state.memory = load_memory(
        st.session_state.chat_id
    )
def switch_conversation(chat_id):
    st.session_state.chat_id = chat_id
    st.session_state.memory = load_memory(chat_id)
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

.stApp {
    background: #f5f7ff;
    color: #20243a;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(245,247,255,0.92);
}

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e6e9f5;
}

[data-testid="stSidebar"] * {
    color: #303650;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2.5rem;
    max-width: 1180px;
}

h1, h2, h3, p, label {
    color: #20243a;
}

.hero {
    background: linear-gradient(120deg, #e9eaff, #e6f5ff);
    border: 1px solid #dce3ff;
    border-radius: 24px;
    padding: 28px 32px;
    margin-bottom: 20px;
}

.hero h1 {
    color: #24294b;
    font-size: 2.15rem;
    margin-bottom: 6px;
}

.hero p {
    color: #626b8b;
    margin-bottom: 0;
}

.feature-card {
    background: #ffffff;
    border: 1px solid #e5e9f5;
    border-radius: 17px;
    padding: 17px;
    min-height: 112px;
    box-shadow: 0 4px 16px rgba(50, 60, 110, 0.04);
}

.feature-card b {
    color: #343b68;
}

.feature-card span {
    color: #747c98;
    font-size: 0.9rem;
}

.status-card {
    background: #ffffff;
    border: 1px solid #e5e9f5;
    border-radius: 14px;
    padding: 12px 16px;
}

[data-testid="stChatMessage"] {
    background: #ffffff;
    border: 1px solid #e8ebf5;
    border-radius: 18px;
    padding: 12px 16px;
    box-shadow: 0 3px 12px rgba(50, 60, 110, 0.035);
}

[data-testid="stChatMessage"] p {
    color: #252a40 !important;
}

[data-testid="stChatInput"] {
    border-color: #d9def0 !important;
}

[data-testid="stChatInput"] textarea {
    color: #252a40 !important;
    background: #ffffff !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #8991aa !important;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 12px;
    border: 1px solid #dce1f4;
    background: #f0f2ff;
    color: #343b68;
    font-weight: 600;
    min-height: 2.6rem;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: #aab4f4;
    background: #e5e9ff;
    color: #29305f;
}

div[data-testid="stAlert"] {
    border-radius: 14px;
}

hr {
    border-color: #e8ebf5;
}

.small-note {
    color: #7b829b;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)
with st.sidebar:
    st.markdown("## 🌐 MemoSphere")
    st.caption("Your conversations. Your memory. Your AI.")
    st.divider()
    if st.button(
        "＋ New conversation",
        use_container_width=True
    ):
        new_id = create_conversation()
        switch_conversation(new_id)
        st.rerun()
    st.markdown("### Your conversations")
    search_text = st.text_input(
        "🔎 Search chats",
        placeholder="Search conversation titles..."
    )
    conversations = get_conversations()
    if search_text.strip():
        conversations = [
            chat for chat in conversations
            if search_text.lower() in chat["title"].lower()
        ]
    if conversations:
        for chat in conversations:
            is_current = (
                chat["id"] == st.session_state.chat_id
            )
            button_label = (
                ("● " if is_current else "  ")
                + chat["title"]
            )
            if st.button(
                button_label,
                key=f"open_{chat['id']}",
                use_container_width=True
            ):
                if chat["id"] != st.session_state.chat_id:
                    switch_conversation(chat["id"])
                    st.rerun()
    else:
        st.caption("No matching conversations found.")
    st.divider()
    st.markdown("### 🧠 Memory system")
    st.markdown("""
    **ConversationBufferMemory**

    Keeps earlier messages available as context.

    **SQLite storage**

    Saves your conversations locally on your computer.
    """)
    if st.button(
        "🗑 Clear current conversation",
        use_container_width=True
    ):
        clear_conversation(st.session_state.chat_id)
        st.session_state.memory.clear()
        st.rerun()
    st.divider()
    st.caption("⚡ Powered by Ollama")
    st.caption(f"Model: `{DEFAULT_MODEL}`")
    st.caption("🔒 Local conversation database")
st.markdown("""
<div class="hero">

    <h1>✨ Welcome to MemoSphere AI</h1>

    <p>
        Your intelligent AI companion that remembers conversations
        and helps you continue right where you left off.
    </p>

</div>
""", unsafe_allow_html=True)
status_col, model_col = st.columns([1, 1])
with status_col:
    if ollama_is_running():
        st.success("● Ollama is connected")
    else:
        st.error("● Ollama is not responding")
with model_col:
    st.info(f"🤖 Active model: {DEFAULT_MODEL}")
card1, card2, card3 = st.columns(3)
with card1:
    st.markdown("""
    <div class="feature-card">
        <b>💬 Context-aware chat</b><br>
        <span>
            Continue conversations without repeating everything.
        </span>
    </div>
    """, unsafe_allow_html=True)

with card2:
    st.markdown("""
    <div class="feature-card">
        <b>💾 Saved history</b><br>
        <span>
            Return to previous conversations whenever you need.
        </span>
    </div>
    """, unsafe_allow_html=True)

with card3:
    st.markdown("""
    <div class="feature-card">
        <b>📄 Chat export</b><br>
        <span>
            Download the current conversation as a text file.
        </span>
    </div>
    """, unsafe_allow_html=True)
st.markdown("")
st.divider()
current_messages = get_messages(
    st.session_state.chat_id
)
if current_messages:
    export_lines = [
        "MemoSphere AI Conversation",
        "=" * 28,
        ""
    ]
    for message in current_messages:
        role = (
            "You"
            if message["role"] == "user"
            else "MemoSphere"
        )
        export_lines.append(
            f"{role}:\n{message['content']}\n"
        )
    export_text = "\n".join(export_lines)
    download_col, info_col = st.columns([1, 3])
    with download_col:
        st.download_button(
            label="⬇️ Export conversation",
            data=export_text,
            file_name="memosphere_conversation.txt",
            mime="text/plain",
            use_container_width=True
        )
    with info_col:
        st.caption(
            "Download this chat as a .txt file and keep a copy."
        )
else:
    st.caption(
        "Start chatting below. Your conversation will appear here."
    )
if not current_messages:
    st.markdown(
        "### 👋 Hello! What would you like to talk about?"
    )
    example1, example2, example3 = st.columns(3)
    with example1:
        st.markdown("""
        <div class="feature-card">
            <b>💡 Learn</b><br>
            <span>
                Explain artificial intelligence in simple words.
            </span>
        </div>
        """, unsafe_allow_html=True)

    with example2:
        st.markdown("""
        <div class="feature-card">
            <b>✍️ Create</b><br>
            <span>
                Help me write a professional email.
            </span>
        </div>
        """, unsafe_allow_html=True)

    with example3:
        st.markdown("""
        <div class="feature-card">
            <b>🧩 Explore</b><br>
            <span>
                Suggest a beginner-friendly Python project.
            </span>
        </div>
        """, unsafe_allow_html=True)
for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
prompt = st.chat_input("Message MemoSphere...")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("MemoSphere is thinking..."):
            try:
                answer = ask_memosphere(prompt)
                st.markdown(answer)
                save_conversation(
                    st.session_state.chat_id,
                    prompt,
                    answer
                )
            except Exception as exc:
                st.error(
                    "Could not generate a response. "
                    "Check that Ollama is running and that "
                    f"{DEFAULT_MODEL} is installed.\n\n"
                    f"Details: {exc}"
                )
    st.rerun()