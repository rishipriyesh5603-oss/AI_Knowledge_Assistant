import os
import requests
import tempfile
import streamlit as st

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "https://ai-knowledge-assistant-1-po9j.onrender.com"
).rstrip("/")
st.write("BACKEND URL:", BACKEND_URL)

def get_documents(user_id):
    try:
        response = requests.get(
            f"{BACKEND_URL}/documents/{user_id}",
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            return (
                data.get("documents", []),
                data.get("chunk_count", 0)
            )

    except requests.RequestException:
        pass

    return [], 0

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="RAG AI Knowledge Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# ADVANCED UI CSS
# =========================================================

st.markdown("""
<style>

/* =========================================================
   RISHI AI — DARK PREMIUM THEME
   ========================================================= */

:root {
    --bg: #060915;
    --bg2: #071023;
    --panel: #0a1429;
    --panel2: #0d1930;
    --border: #1c3150;

    --text: #f5f7ff;
    --muted: #8d9bb5;

    --cyan: #29d9ff;
    --blue: #4d8dff;
    --purple: #735cff;

    --glow: rgba(41, 217, 255, 0.18);
}


/* =========================================================
   APP BACKGROUND
   ========================================================= */

[data-testid="stAppViewContainer"] {

    background:
        radial-gradient(
            circle at 85% 8%,
            rgba(39, 105, 255, 0.14),
            transparent 25%
        ),
        radial-gradient(
            circle at 15% 55%,
            rgba(41, 217, 255, 0.06),
            transparent 25%
        ),
        linear-gradient(
            180deg,
            #060915 0%,
            #071023 48%,
            #060b19 100%
        );

    color: var(--text);
}


/* =========================================================
   HEADER
   ========================================================= */

[data-testid="stHeader"] {
    background: transparent;
}


/* =========================================================
   MAIN CONTENT
   ========================================================= */

.block-container {

    max-width: 1450px;

    padding-top: 2rem;
    padding-bottom: 6rem;
}


/* =========================================================
   TYPOGRAPHY
   ========================================================= */

h1 {

    color: #f8fbff !important;

    font-size: 54px !important;

    font-weight: 800 !important;

    letter-spacing: -2.5px !important;

    line-height: 1.05 !important;
}


h2 {

    color: #f5f8ff !important;

    font-weight: 750 !important;

}


h3 {

    color: #e8efff !important;

}


p {

    color: var(--muted);

}


/* =========================================================
   GRADIENT TEXT
   ========================================================= */

.gradient-text {

    background:
        linear-gradient(
            90deg,
            #ffffff 0%,
            #ffffff 38%,
            #36ddff 67%,
            #5b8cff 100%
        );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #070b18,
            #081124
        );

    border-right: 1px solid #172742;
}


section[data-testid="stSidebar"] * {

    color: #dce7f7;
}


/* Sidebar title */

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {

    color: #f7fbff !important;
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button {
    background: #101b2d;

    color: #aebed2;

    border: 1px solid #263a53;

    border-radius: 12px;

    min-height: 42px;

    font-weight: 600;

    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #15243a;

    color: #d5e4f2;

    border-color: #355673;

    box-shadow:
        0 4px 15px rgba(0, 0, 0, 0.18);
}


/* Primary button */

button[kind="primary"] {
    background: #17344b !important;

    color: #c7d8e8 !important;

    border: 1px solid #2b536d !important;

    font-weight: 600 !important;

    box-shadow:
        0 5px 16px rgba(0, 0, 0, 0.22) !important;
}

button[kind="primary"]:hover {
    background: #1c405a !important;

    color: #e5f1fa !important;

    border-color: #396a87 !important;

    box-shadow:
        0 6px 20px rgba(41, 217, 255, 0.08) !important;
}

/* =========================================================
   METRIC CARDS
   ========================================================= */

[data-testid="stMetric"] {

    background:
        linear-gradient(
            145deg,
            rgba(13, 27, 51, 0.92),
            rgba(8, 19, 38, 0.92)
        );

    border: 1px solid #1d3453;

    border-radius: 18px;

    padding: 20px;

    box-shadow:
        inset 0 1px rgba(255,255,255,0.025),
        0 12px 35px rgba(0,0,0,0.20);

    transition: 0.2s ease;
}


[data-testid="stMetric"]:hover {

    border-color: #31577e;

    transform: translateY(-2px);

}


[data-testid="stMetricLabel"] {

    color: #8192ad !important;

}


[data-testid="stMetricValue"] {

    color: #f5f9ff !important;

}


/* =========================================================
   CHAT
   ========================================================= */

[data-testid="stChatMessage"] {

    background:
        rgba(9, 20, 39, 0.86);

    border:

        1px solid #1c304d;

    border-radius: 18px;

    margin-bottom: 14px;

    padding: 10px;

    box-shadow:
        0 8px 30px rgba(0,0,0,0.16);
}


/* User message */

[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarUser"]
) {

    background:
        linear-gradient(
            145deg,
            rgba(22, 34, 68, 0.95),
            rgba(12, 22, 45, 0.95)
        );

    border-color: #293d66;
}


/* AI message */

[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarAssistant"]
) {

    background:
        linear-gradient(
            145deg,
            rgba(9, 25, 45, 0.95),
            rgba(7, 18, 34, 0.95)
        );

    border-color: #1b4056;
}


/* Chat text */

[data-testid="stChatMessage"] p {

    color: #dce7f7;

}


/* =========================================================
   CHAT INPUT — EXACT STREAMLIT TARGET
   ========================================================= */

textarea[placeholder="Ask anything about your documents..."] {
    background: #0b1629 !important;
    color: #e2e8f0 !important;
    border: none !important;
    box-shadow: none !important;
}

/* Placeholder text */
textarea[placeholder="Ask anything about your documents..."]::placeholder {
    color: #9aa8ba !important;
    -webkit-text-fill-color: #9aa8ba !important;
    opacity: 1 !important;
}

/* Outer chat box */
[data-testid="stChatInput"] {
    background: #0a1323 !important;
    border: 1px solid #1d3048 !important;
    border-radius: 18px !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25) !important;
}

/* Send button */
[data-testid="stChatInput"] button {
    background: #172235 !important;
    color: #aeb9c8 !important;
    border: 1px solid #27384e !important;
    border-radius: 10px !important;
}

/* Send button hover */
[data-testid="stChatInput"] button:hover {
    background: #202f44 !important;
    color: #d8e2ec !important;
    border-color: #3a526b !important;
}


/* =========================================================
   TEXT INPUT
   ========================================================= */

input,
textarea {

    background: #091326 !important;

    color: #edf5ff !important;

    border-color: #29405d !important;

    border-radius: 11px !important;
}


input:focus,
textarea:focus {

    border-color: #29d9ff !important;

    box-shadow:
        0 0 0 1px rgba(41,217,255,0.25) !important;
}


input::placeholder,
textarea::placeholder {

    color: #64748b !important;
}


/* =========================================================
   FILE UPLOADER
   ========================================================= */

[data-testid="stFileUploader"] {

    background: #091326;

    border: 1px solid #213a57;

    border-radius: 15px;

    padding: 8px;
}


[data-testid="stFileUploader"] section {

    background: #0b172c;

    border-color: #29405d;
}


/* =========================================================
   EXPANDERS
   ========================================================= */

[data-testid="stExpander"] {

    background: #091528;

    border: 1px solid #203753;

    border-radius: 13px;
}


[data-testid="stExpander"] summary {

    color: #cfe0f5;
}


/* =========================================================
   TABS
   ========================================================= */

button[data-baseweb="tab"] {

    color: #7f91aa !important;

    font-weight: 650;
}


button[data-baseweb="tab"][aria-selected="true"] {

    color: #32dcff !important;
}


/* =========================================================
   ALERTS
   ========================================================= */

[data-testid="stAlert"] {

    background: #0b172b;

    border: 1px solid #24405e;

    border-radius: 14px;
}


/* =========================================================
   DIVIDERS
   ========================================================= */

hr {

    border-color: #172b46;

}


/* =========================================================
   SCROLLBAR
   ========================================================= */

::-webkit-scrollbar {

    width: 7px;

}


::-webkit-scrollbar-track {

    background: #050914;

}


::-webkit-scrollbar-thumb {

    background: #1d3451;

    border-radius: 10px;

}


::-webkit-scrollbar-thumb:hover {

    background: #2b5d87;

}


/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 900px) {

    h1 {

        font-size: 38px !important;

    }

    .block-container {

        padding-left: 1rem;

        padding-right: 1rem;

    }

}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

if "current_page" not in st.session_state:
    st.session_state.current_page = "Chat"


# =========================================================
# AUTHENTICATION
# =========================================================

if not st.session_state.authenticated:

    st.title("🤖 RAG AI Assistant")

    st.caption(
        "Your private AI-powered knowledge assistant"
    )

    st.write("")

    login_tab, register_tab = st.tabs(
        [
            "🔐 Login",
            "✨ Create Account"
        ]
    )


    # =====================================================
    # LOGIN
    # =====================================================

    with login_tab:

        st.subheader("Welcome back")

        st.caption(
            "Login to access your personal knowledge base."
        )

        st.write("")

        with st.form(
            "login_form",
            clear_on_submit=False
        ):

            username = st.text_input(
                "Username or Email",
                key="login_username"
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )

            st.write("")

            login_submitted = st.form_submit_button(
                "🔐 Login",
                use_container_width=True,
                type="primary"
            )


        if login_submitted:

            if not username or not password:

                st.error(
                    "Please enter your username and password."
                )

            else:

                try:
                    response = requests.post(
                        f"{BACKEND_URL}/auth/login",
                        json={
                            "username": username,
                            "password": password
                        },
                        timeout=60
                    )

                    if response.status_code == 200:
                        user = response.json().get("user")

                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.session_state.messages = []

                            st.session_state.processed_files = (
                                get_documents(user["id"])[0]
                            )

                            st.rerun()
                        else:
                            st.error("Login failed.")

                    elif response.status_code == 401:
                        st.error("Invalid username/email or password.")

                    else:
                        try:
                            error_data = response.json()
                            error_message = error_data.get(
                                "detail",
                                f"Login failed. Server returned {response.status_code}."
                            )
                        except ValueError:
                            error_message = (
                                f"Login failed. Server returned {response.status_code} "
                                f"with non-JSON response."
                            )

                        st.error(error_message)

                except requests.RequestException as e:
                    st.error(f"Could not connect to backend: {e}")




    # =====================================================
    # REGISTER
    # =====================================================

    with register_tab:

        st.subheader("Create your account")

        st.caption(
            "Build your private AI knowledge workspace."
        )

        st.write("")

        with st.form(
            "register_form",
            clear_on_submit=False
        ):

            new_username = st.text_input(
                "Username",
                key="register_username"
            )

            new_email = st.text_input(
                "Email",
                key="register_email"
            )

            new_password = st.text_input(
                "Password",
                type="password",
                key="register_password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                key="confirm_password"
            )

            st.write("")

            register_submitted = st.form_submit_button(
                "✨ Create Account",
                use_container_width=True,
                type="primary"
            )


        if register_submitted:

            if not new_username:

                st.error(
                    "Username is required."
                )

            elif not new_email:

                st.error(
                    "Email is required."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                try:
                    response = requests.post(
                        f"{BACKEND_URL}/auth/register",
                        json={
                            "username": new_username,
                            "email": new_email,
                            "password": new_password
                        },
                        timeout=60
                    )

                    if response.status_code == 200:
                        data = response.json()

                        st.success(
                            data.get(
                                "message",
                                "Account created successfully."
                            )
                        )

                        st.info(
                            "Your account is ready. Go to Login."
                        )

                    else:
                        st.error(
                            response.json().get(
                                "detail",
                                "Registration failed."
                            )
                        )

                except requests.RequestException as e:
                    st.error(
                        f"Could not connect to backend: {e}"
                    )

# =========================================================
# CURRENT USER
# =========================================================

# Safety check:
# If authentication state is invalid, return to login.

user = st.session_state.get("user")
if user is None:
    st.session_state.authenticated=False
    st.stop()

user_id=user["id"]
username=user["username"]
email=user["email"]

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # -----------------------------------------------------
    # BRAND
    # -----------------------------------------------------

    st.title("🤖 RAG AI")

    st.caption(
        "Knowledge Assistant"
    )

    st.divider()


    # -----------------------------------------------------
    # NAVIGATION
    # -----------------------------------------------------

    st.markdown("### WORKSPACE")

    if st.button(
        "💬  AI Chat",
        use_container_width=True
    ):

        st.session_state.current_page = "Chat"

        st.rerun()


    if st.button(
        "📄  Documents",
        use_container_width=True
    ):

        st.session_state.current_page = "Documents"

        st.rerun()


    st.divider()


    # -----------------------------------------------------
    # UPLOAD
    # -----------------------------------------------------

    st.markdown("### KNOWLEDGE BASE")

    uploaded_files = st.file_uploader(
        "Add PDF documents",
        type=["pdf"],
        accept_multiple_files=True
    )


    if uploaded_files:

        if st.button(
            "⚡ Index Documents",
            use_container_width=True,
            type="primary"
        ):

            total_chunks = 0

            progress = st.progress(0)

            status = st.empty()


            for index, uploaded_file in enumerate(
                uploaded_files
            ):

                status.info(
                    f"Processing {uploaded_file.name}"
                )


                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as temp_file:

                    temp_file.write(
                        uploaded_file.getbuffer()
                    )

                    temp_path = temp_file.name


                try:

                    with open(temp_path, "rb") as pdf_file:

                        response = requests.post(
                            f"{BACKEND_URL}/documents/upload/{user_id}",
                            files={
                                "file": (
                                    uploaded_file.name,
                                    pdf_file,
                                    "application/pdf"
                                )
                            },
                            timeout=300
                        )

                    if response.status_code == 200:

                        data = response.json()

                        chunks = data.get("chunks", 0)

                        total_chunks += chunks

                    else:

                        try:
                            error_message = response.json().get(
                                "detail",
                                f"Document upload failed. Server returned {response.status_code}."
                            )
                        except ValueError:
                            error_message = (
                                f"Document upload failed. Server returned "
                                f"{response.status_code}."
                            )

                        st.error(error_message)
                        chunks = 0

                finally:

                    os.remove(temp_path)


                progress.progress(
                    (index + 1) /
                    len(uploaded_files)
                )


            status.success(
                f"✓ Indexed {total_chunks} chunks"
            )

            st.session_state.processed_files = (
                get_documents(user_id)
            )


    # -----------------------------------------------------
    # USER DOCUMENTS
    # -----------------------------------------------------

    st.divider()

    sources, chunk_count = get_documents(user_id)
    st.markdown(
        f"### 📚 Your Files ({len(sources)})"
    )

    if sources:

        for source in sources:

            st.write(
                f"📄 {source}"
            )

    else:

        st.caption(
            "No documents indexed."
        )


    # -----------------------------------------------------
    # USER ACCOUNT
    # -----------------------------------------------------

    st.divider()

    st.markdown("### 👤 Account")

    st.write(
        f"**{username}**"
    )

    st.caption(email)


    # -----------------------------------------------------
    # LOGOUT
    # -----------------------------------------------------

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.authenticated = False

        st.session_state.user = None

        st.session_state.messages = []

        st.session_state.processed_files = []

        st.rerun()


# =========================================================
# MAIN PAGE
# =========================================================

sources, chunk_count = get_documents(user_id)


# =========================================================
# TOP HEADER
# =========================================================

st.markdown(
    "### 01 / KNOWLEDGE ASSISTANT"
)

st.markdown(
    f"""
    # Your documents.<br>
    Your knowledge.<br>
    <span style="color:#29d9ff;">
    Your AI assistant.
    </span>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Ask questions, discover information and understand "
    "your documents with AI."
)

st.write("")


# =========================================================
# DASHBOARD METRICS
# =========================================================

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    st.metric(
        "DOCUMENTS",
        len(sources)
    )

with metric2:
    st.metric(
        "CHUNKS",
        chunk_count
    )

with metric3:
    st.metric(
        "RAG STATUS",
        "READY" if chunk_count > 0 else "EMPTY"
    )

with metric4:
    st.metric(
        "MODEL",
        "LLAMA 3.3 70B"
    )


st.write("")


# =========================================================
# DOCUMENT PAGE
# =========================================================

if st.session_state.current_page == "Documents":

    st.header("📄 Your Documents")

    st.caption(
        "Manage the documents available to your RAG assistant."
    )


    if sources:

        for source in sources:

            col1, col2 = st.columns(
                [5, 1]
            )

            with col1:

                st.info(
                    f"📄 **{source}**\n\n"
                    "Status: 🟢 Indexed"
                )

            with col2:

                st.write("")

                st.write("")


        st.divider()

        st.subheader(
            "Knowledge Base"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Indexed chunks",
                chunk_count
            )

        with col2:

            st.metric(
                "Documents",
                len(sources)
            )


        st.write("")

        if st.button(
            "⚠️ Delete All My Documents",
            type="secondary"
        ):

            try:

                response = requests.delete(
                    f"{BACKEND_URL}/documents/{user_id}",
                    timeout=60
                )

                if response.status_code == 200:

                    deleted = response.json().get(
                        "deleted_chunks",
                        0
                    )

                    st.session_state.processed_files = []

                    st.success(
                        f"Deleted {deleted} chunks."
                    )

                    st.rerun()

                else:
                    try:
                        error_message = response.json().get(
                            "detail",
                            f"Failed to delete documents. "
                            f"Server returned {response.status_code}."
                        )
                    except ValueError:
                        error_message = (
                            f"Failed to delete documents. "
                            f"Server returned {response.status_code}."
                        )

                    st.error(error_message)

            except requests.RequestException as e:

                st.error(
                    f"Could not connect to backend: {e}"
                )

                st.rerun()

    else:

        st.info(
            "📚 No documents yet. "
            "Upload PDFs from the sidebar to build your knowledge base."
        )


# =========================================================
# CHAT PAGE
# =========================================================

else:

    # -----------------------------------------------------
    # EMPTY CHAT
    # -----------------------------------------------------

    if not st.session_state.messages:

        st.subheader(
            "What can I help you find? 🧠"
        )

        st.caption(
            "Your answers are generated using your indexed documents."
        )

        st.write("")


        # ================================================
        # FEATURE CARDS
        # ================================================

        c1, c2, c3 = st.columns(3)


        with c1:

            st.info(
                """
                ### 📚 Understand

                Ask questions about your
                uploaded documents.
                """
            )


        with c2:

            st.info(
                """
                ### 🔎 Search

                Find relevant information
                across your knowledge base.
                """
            )


        with c3:

            st.info(
                """
                ### ⚡ Summarize

                Quickly extract the most
                important information.
                """
            )


        st.write("")

        st.subheader(
            "✨ Try asking"
        )


        q1, q2, q3 = st.columns(3)


        suggestions = [
            "Summarize my documents",
            "What are the key points?",
            "Explain the main concepts"
        ]


        for column, suggestion in zip(
            [q1, q2, q3],
            suggestions
        ):

            with column:

                if st.button(
                    suggestion,
                    use_container_width=True
                ):

                    st.session_state.suggested_question = (
                        suggestion
                    )

                    st.rerun()


    # -----------------------------------------------------
    # CHAT HISTORY
    # -----------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"],
            avatar=(
                "👤"
                if message["role"] == "user"
                else "🤖"
            )
        ):

            st.markdown(
                message["content"]
            )


            sources_used = message.get(
                "sources",
                []
            )


            if sources_used:

                with st.expander(
                    f"📚 {len(sources_used)} sources used"
                ):

                    for source in sources_used:

                        st.write(
                            f"📄 **{source['source']}** "
                            f"• Page {source['page']}"
                        )


    # -----------------------------------------------------
    # CHAT INPUT
    # -----------------------------------------------------

    question = st.chat_input(
        "Ask anything about your documents..."
    )


    if (
        not question
        and "suggested_question"
        in st.session_state
    ):

        question = (
            st.session_state.suggested_question
        )

        del st.session_state.suggested_question


    # -----------------------------------------------------
    # PROCESS QUESTION
    # -----------------------------------------------------

    if question:

        st.session_state.messages.append({

            "role": "user",

            "content": question

        })


        with st.chat_message(
            "user",
            avatar="👤"
        ):

            st.markdown(
                question
            )


        # ================================================
        # NO DOCUMENTS
        # ================================================

        if chunk_count == 0:

            answer = (
                "📚 **Your knowledge base is empty.**\n\n"
                "Upload and index a PDF from the sidebar first."
            )


            with st.chat_message(
                "assistant",
                avatar="🤖"
            ):

                st.markdown(
                    answer
                )


            st.session_state.messages.append({

                "role": "assistant",

                "content": answer,

                "sources": []

            })


        # ================================================
        # RAG
        # ================================================

        else:

            with st.chat_message(
                "assistant",
                avatar="🤖"
            ):

                with st.spinner(
                    "🔎 Searching your knowledge base..."
                ):

                    try:

                        response = requests.post(
                            f"{BACKEND_URL}/chat",
                            json={
                                "user_id": user_id,
                                "question": question
                            },
                            timeout=180
                        )

                        if response.status_code != 200:
                            raise Exception(
                                response.json().get(
                                    "detail",
                                    "RAG request failed."
                                )
                            )

                        data = response.json()

                        answer = data.get(
                            "answer",
                            "No answer returned."
                        )

                        retrieved_documents = data.get(
                            "sources",
                            []
                        )
                        st.markdown(
                            answer
                        )


                        if retrieved_documents:

                            with st.expander(
                                f"📚 "
                                f"{len(retrieved_documents)} "
                                f"sources used"
                            ):

                                for source in (
                                    retrieved_documents
                                ):

                                    st.write(
                                        f"📄 "
                                        f"**{source['source']}** "
                                        f"• Page "
                                        f"{source['page']}"
                                    )


                        st.session_state.messages.append({

                            "role": "assistant",

                            "content": answer,

                            "sources": (
                                retrieved_documents
                            )

                        })


                    except Exception as e:

                        error = (
                            "❌ Something went wrong.\n\n"
                            f"`{str(e)}`"
                        )


                        st.error(
                            error
                        )


                        st.session_state.messages.append({

                            "role": "assistant",

                            "content": error,

                            "sources": []

                        })


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🤖 RAG AI Knowledge Assistant • "
    "Powered by ChromaDB + GROQ + FastAPI"
)