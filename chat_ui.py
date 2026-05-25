import streamlit as st
from client.gemini_mcp_client import ask

# -------------------------------------------------
# Page config
# -------------------------------------------------

st.set_page_config(
    page_title="Alteryx FP&A Variance Assistant",
    page_icon="📊",
    layout="centered",
)

# -------------------------------------------------
# Alteryx One styling
# -------------------------------------------------

st.markdown("""
<style>

/* ---------- Global ---------- */
.stApp {
    background-color: #0E1117;
    color: #E5E7EB;
    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont;
}

/* ---------- Header ---------- */
h1 {
    color: #E5E7EB;
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.caption {
    color: #9CA3AF;
    font-size: 0.9rem;
    margin-bottom: 1.25rem;
}

/* ---------- Suggested Questions ---------- */
.suggested-container {
    margin-bottom: 1.5rem;
}

.suggested-title {
    color: #9CA3AF;
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
}

.suggested-btn button {
    background-color: #0B1220 !important;
    color: #E5E7EB !important;
    border: 1px solid #1F2937 !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
}

.suggested-btn button:hover {
    border-color: #00B3A4 !important;
    color: #00B3A4 !important;
}

/* ---------- Chat layout ---------- */
.chat-card-user {
    background-color: #111827;
    border-left: 3px solid #0072CE;
    padding: 14px 16px;
    border-radius: 6px;
    margin-bottom: 10px;
}

.chat-card-ai {
    background-color: #0B1220;
    border-left: 3px solid #00B3A4;
    padding: 14px 16px;
    border-radius: 6px;
    margin-bottom: 16px;
}

/* ---------- Expanders ---------- */
details summary {
    color: #9CA3AF;
    font-size: 0.85rem;
}

details {
    background-color: #0B1220;
    border-radius: 6px;
    padding: 8px 12px;
}

/* ---------- Input ---------- */
textarea {
    background-color: #0B1220 !important;
    color: #E5E7EB !important;
    border: 1px solid #1F2937 !important;
    border-radius: 8px !important;
}

textarea:focus {
    border-color: #00B3A4 !important;
    box-shadow: none !important;
}

/* ---------- Footer ---------- */
.footer {
    color: #6B7280;
    font-size: 0.75rem;
    margin-top: 2rem;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Header
# -------------------------------------------------

st.title("Alteryx FP&A Variance Assistant")
st.markdown(
    "<div class='caption'>Budget vs actual analysis, trend detection, and variance drivers powered by Alteryx and Google Cloud</div>",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Suggested Questions Panel (NEW)
# -------------------------------------------------

SUGGESTED_QUESTIONS = [
    "What are the biggest overspends for September 2025?",
    "What spending trends shifted significantly in September 2025?",
    "Explain the main drivers of overspend in September 2025",
    "What explains the variance for Marketing in September 2025?",
]

st.markdown("<div class='suggested-title'>Suggested questions</div>", unsafe_allow_html=True)

cols = st.columns(len(SUGGESTED_QUESTIONS))
for i, q in enumerate(SUGGESTED_QUESTIONS):
    with cols[i]:
        if st.button(q, key=f"suggested_{i}", use_container_width=True):
            st.session_state.pending_question = q

st.markdown("<div class='suggested-container'></div>", unsafe_allow_html=True)

# -------------------------------------------------
# Session state
# -------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# -------------------------------------------------
# Render chat history
# -------------------------------------------------

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='chat-card-user'>{msg['content']}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='chat-card-ai'>{msg['content']}</div>",
            unsafe_allow_html=True,
        )

        if "data" in msg and msg["data"]:
            with st.expander("View supporting data"):
                st.json(msg["data"])

# -------------------------------------------------
# Input handling
# -------------------------------------------------

user_input = st.chat_input("Ask an FP&A question (e.g. Explain overspend in Sep 2025)")

# Prefer suggested question if clicked
if st.session_state.pending_question:
    user_input = st.session_state.pending_question
    st.session_state.pending_question = None

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    st.markdown(
        f"<div class='chat-card-user'>{user_input}</div>",
        unsafe_allow_html=True,
    )

    with st.spinner("Analyzing…"):
        try:
            response = ask(user_input)

            commentary = response.get("commentary", "")
            data = response.get("data", {})

            st.markdown(
                f"<div class='chat-card-ai'>{commentary}</div>",
                unsafe_allow_html=True,
            )

            if data:
                with st.expander("View supporting data"):
                    st.json(data)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": commentary,
                    "data": data,
                }
            )

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)

            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg}
            )

# -------------------------------------------------
# Footer
# -------------------------------------------------

st.markdown(
    "<div class='footer'>Demo experience inspired by Alteryx One • Deterministic data • AI-assisted narrative</div>",
    unsafe_allow_html=True,
)
