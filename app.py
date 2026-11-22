import os
import io
import textwrap
import streamlit as st

from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Just4All | Justice for Everyone",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_html(content):
    """Render HTML without Markdown treating indented lines as code."""
    clean_content = "\n".join(line.lstrip() for line in content.splitlines())
    st.markdown(clean_content, unsafe_allow_html=True)


# =====================================================
# 2. CUSTOM CSS
# =====================================================

render_html("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #F5F7FB;
    color: #142544;
}

/* Main content */

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Text visibility */

.main p,
.main label,
.main li {
    color: #263750;
}

/* Headings */

h1, h2, h3, h4 {
    color: #142544 !important;
    font-weight: 700;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background-color: #101D35;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF;
}

section[data-testid="stSidebar"] h2 {
    color: #F0C76A !important;
}

section[data-testid="stSidebar"] p {
    color: #FFFFFF !important;
}

/* Sidebar navigation */

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    color: #FFFFFF !important;
    border-radius: 8px;
    padding: 8px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: #FFFFFF !important;
}

/* Text area */

.stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #142544 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px;
}

.stTextArea textarea::placeholder {
    color: #64748B !important;
}

/* Text input */

.stTextInput input {
    background-color: #FFFFFF !important;
    color: #142544 !important;
    border-radius: 10px;
}

/* Selectbox */

.stSelectbox div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
}

.stSelectbox div[data-baseweb="select"] * {
    color: #142544 !important;
}

/* Buttons */

.stButton > button {
    background-color: #D5A947;
    color: #142544 !important;
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 700;
}

.stButton > button:hover {
    background-color: #BD9135;
    color: #FFFFFF !important;
}

/* Feature cards */

.feature-card {
    background-color: #FFFFFF;
    padding: 24px;
    border-radius: 15px;
    border: 1px solid #E5EAF2;
    min-height: 175px;
    box-shadow: 0 3px 12px rgba(20,37,68,0.05);
    margin-bottom: 15px;
}

.feature-card h3 {
    color: #142544 !important;
}

.feature-card p {
    color: #64748B !important;
}

/* Hero section */

.hero {
    background: linear-gradient(120deg, #101D35, #243F68);
    padding: 45px 35px;
    border-radius: 20px;
    margin-bottom: 25px;
}

.hero h1 {
    color: #FFFFFF !important;
    font-size: 38px;
}

.hero p {
    color: #E0E8F5 !important;
    font-size: 17px;
}

.hero-tag {
    color: #F0C76A !important;
    font-weight: 700;
    letter-spacing: 2px;
}

/* Download button */

.stDownloadButton > button {
    background-color: #142544;
    color: #FFFFFF !important;
    border-radius: 10px;
}

/* Chat messages */

[data-testid="stChatMessage"] {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E5EAF2;
}

/* Chat input */

[data-testid="stChatInput"] textarea {
    background-color: #FFFFFF !important;
    color: #142544 !important;
}

/* Disclaimer */

.disclaimer {
    background-color: #FFF7E6;
    border-left: 4px solid #D5A947;
    padding: 15px;
    border-radius: 8px;
    color: #604A20 !important;
    font-size: 13px;
}

/* Divider */

hr {
    border-color: #E2E8F0;
}

</style>
""")


# =====================================================
# 3. GEMINI API CONFIGURATION
# =====================================================

try:

    API_KEY = st.secrets.get(
        "GEMINI_API_KEY",
        os.getenv("GEMINI_API_KEY")
    )

except Exception:

    API_KEY = os.getenv("GEMINI_API_KEY")


MODEL = "gemini-3.5-flash-lite"

client = genai.Client(api_key=API_KEY) if API_KEY else None


# =====================================================
# 4. GEMINI RESPONSE FUNCTION
# =====================================================

def ask_gemini(prompt):

    if not client:
        return "Gemini API key is missing. Please configure your API key."

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        if response.text:
            return response.text

        return "The AI returned an empty response. Please try again."

    except Exception as e:

        return f"Unable to generate a response right now: {str(e)}"


# =====================================================
# 5. PDF GENERATION FUNCTION
# =====================================================

def create_pdf(content):

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    y = height - 60

    pdf.setFont("Helvetica-Bold", 20)

    pdf.drawString(50, y, "Just4All")

    y -= 25

    pdf.setFont("Helvetica", 10)

    pdf.drawString(
        50,
        y,
        "Justice for Everyone. Rights Within Reach."
    )

    y -= 35

    pdf.setFont("Helvetica", 10)

    for paragraph in content.split("\n"):

        lines = textwrap.wrap(
            paragraph,
            width=90
        ) or [""]

        for line in lines:

            if y < 60:

                pdf.showPage()

                y = height - 60

                pdf.setFont("Helvetica", 10)

            pdf.drawString(50, y, line)

            y -= 15

    pdf.save()

    buffer.seek(0)

    return buffer


# =====================================================
# 6. COMMON AI INSTRUCTIONS
# =====================================================

SYSTEM_CONTEXT = """
You are Just4All, an AI-powered Indian legal information assistant.

Your mission is to make legal information accessible to everyone.

Instructions:

1. Explain Indian laws in simple language.
2. Never invent legal sections or court judgments.
3. Distinguish verified information from general guidance.
4. Mention official government sources where possible.
5. Explain uncertainty when information is incomplete.
6. Never guarantee legal outcomes.
7. Protect the user's privacy.
8. Recommend qualified legal assistance when necessary.
9. Do not pretend to replace a lawyer.
10. Provide general legal information, not professional legal advice.
"""


# =====================================================
# 7. NAVIGATION FUNCTION
# =====================================================

def navigate_to(page_name):

    st.session_state.page_nav = page_name


# =====================================================
# 8. SIDEBAR NAVIGATION
# =====================================================

if "page_nav" not in st.session_state:
    st.session_state.page_nav = "Home"

with st.sidebar:

    render_html("""
        <div style="text-align:center; padding:15px 0 25px 0;">

            <div style="font-size:45px;">⚖️</div>

            <h2 style="color:#F0C76A;">
                Just4All
            </h2>

            <p style="font-size:11px;">
                JUSTICE FOR EVERYONE
            </p>

        </div>
        """)

    st.markdown("---")

    st.markdown("### Navigation")

    page = st.radio(
        "Choose a feature",
        [
            "Home",
            "Analyze My Problem",
            "Ask Just4All",
            "Legal Action Planner",
            "Document Generator",
            "Know Your Rights"
        ],
        key="page_nav",
        label_visibility="collapsed"
    )

    st.markdown("---")

    language = st.selectbox(
        "🌐 Choose Language",
        ["English", "Malayalam"]
    )

    st.markdown("---")

    render_html("""
        <div style="font-size:12px;">
            <b>Our Mission</b><br><br>
            Making legal knowledge simple,
            accessible and understandable
            for everyone.
        </div>
        """)


# =====================================================
# 9. LANGUAGE INSTRUCTION
# =====================================================

LANGUAGE_CONTEXT = f"""
Respond in {language}.
Use simple and understandable language.
"""


# =====================================================
# 10. HOME PAGE
# =====================================================

if page == "Home":

    render_html("""
        <div class="hero">

            <div class="hero-tag">
                WELCOME TO JUST4ALL
            </div>

            <h1>
                Justice should be accessible to everyone.
            </h1>

            <p>
                Understand your rights. Explore your legal options.
                Take informed action with AI-powered legal guidance.
            </p>

        </div>
        """)

    st.markdown("## Your Legal Companion")

    st.write(
        "Choose a service below to get started with your legal journey."
    )

    # First row

    col1, col2, col3 = st.columns(3)

    with col1:

        render_html("""
            <div class="feature-card">
                <h3>🔍 Legal Analyzer</h3>
                <p>
                Describe your legal problem and understand
                potentially relevant laws and available options.
                </p>
            </div>
            """)

        st.button(
            "Analyze Problem →",
            key="home_analyze",
            use_container_width=True,
            on_click=navigate_to,
            args=('Analyze My Problem',)
        )

    with col2:

        render_html("""
            <div class="feature-card">
                <h3>💬 AI Assistant</h3>
                <p>
                Ask questions and receive simple explanations
                about Indian legal information.
                </p>
            </div>
            """)

        st.button(
            "Ask a Question →",
            key="home_chat",
            use_container_width=True,
            on_click=navigate_to,
            args=('Ask Just4All',)
        )

    with col3:

        render_html("""
            <div class="feature-card">
                <h3>📋 Action Planner</h3>
                <p>
                Get practical steps, evidence checklists
                and guidance on possible next actions.
                </p>
            </div>
            """)

        st.button(
            "Create Action Plan →",
            key="home_plan",
            use_container_width=True,
            on_click=navigate_to,
            args=('Legal Action Planner',)
        )

    # Second row

    col4, col5, col6 = st.columns(3)

    with col4:

        render_html("""
            <div class="feature-card">
                <h3>📄 Document Generator</h3>
                <p>
                Create draft complaint letters
                and other legal documents.
                </p>
            </div>
            """)

        st.button(
            "Generate Document →",
            key="home_document",
            use_container_width=True,
            on_click=navigate_to,
            args=('Document Generator',)
        )

    with col5:

        render_html("""
            <div class="feature-card">
                <h3>⚖️ Know Your Rights</h3>
                <p>
                Explore your basic legal rights
                across different categories.
                </p>
            </div>
            """)

        st.button(
            "Explore Rights →",
            key="home_rights",
            use_container_width=True,
            on_click=navigate_to,
            args=('Know Your Rights',)
        )

    with col6:

        render_html("""
            <div class="feature-card">
                <h3>🌐 Multilingual Support</h3>
                <p>
                Access legal information in English
                and Malayalam.
                </p>
            </div>
            """)

    st.markdown("---")

    st.markdown("## Our Vision")

    st.write(
        """
        We believe that understanding the law should not be difficult.

        Just4All uses AI to make legal information easier to understand,
        regardless of language or background.
        """
    )


# =====================================================
# 11. ANALYZE MY PROBLEM
# =====================================================

elif page == "Analyze My Problem":

    st.title("🔍 AI Legal Problem Analyzer")

    st.write(
        "Describe your situation to understand your possible legal options."
    )

    problem = st.text_area(
        "Describe your legal problem",
        height=180,
        placeholder="Example: My employer has not paid my salary for two months..."
    )

    if st.button("✨ Analyze My Problem"):

        if problem.strip():

            prompt = f"""
            {SYSTEM_CONTEXT}

            {LANGUAGE_CONTEXT}

            Analyze this legal situation under Indian law:

            {problem}

            Use these headings:

            1. Problem Summary
            2. Relevant Legal Area
            3. Potentially Applicable Laws
            4. Possible Rights
            5. Evidence to Collect
            6. Recommended Next Steps
            7. When to Contact a Lawyer
            8. Official Sources to Check

            Do not invent legal provisions.
            Do not assume a law definitely applies without sufficient facts.
            """

            with st.spinner("⚖️ Just4All is analyzing your problem..."):

                result = ask_gemini(prompt)

            st.markdown("---")

            st.subheader("📋 Your Legal Analysis")

            st.markdown(result)

        else:

            st.warning("Please describe your legal problem first.")


# =====================================================
# 12. ASK JUST4ALL
# =====================================================

elif page == "Ask Just4All":

    st.title("💬 Ask Just4All")

    st.write(
        "Your AI legal assistant. Ask questions about Indian law."
    )

    if "messages" not in st.session_state:

        st.session_state.messages = []

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    user_question = st.chat_input(
        "Ask your legal question..."
    )

    if user_question:

        st.session_state.messages.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):

            st.markdown(user_question)

        conversation = ""

        for message in st.session_state.messages[-10:]:

            conversation += (
                f"{message['role']}: {message['content']}\n"
            )

        prompt = f"""
        {SYSTEM_CONTEXT}

        {LANGUAGE_CONTEXT}

        Answer this legal conversation:

        {conversation}

        Give a simple, practical and accurate response.
        """

        with st.chat_message("assistant"):

            with st.spinner("Just4All is thinking..."):

                answer = ask_gemini(prompt)

            st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    if st.button("Clear Conversation"):

        st.session_state.messages = []

        st.rerun()


# =====================================================
# 13. LEGAL ACTION PLANNER
# =====================================================

elif page == "Legal Action Planner":

    st.title("📋 Legal Action Planner")

    st.write(
        "Get a practical step-by-step plan for your legal situation."
    )

    situation = st.text_area(
        "Describe your situation",
        height=180,
        placeholder="Explain what happened..."
    )

    if st.button("✨ Create My Action Plan"):

        if situation.strip():

            prompt = f"""
            {SYSTEM_CONTEXT}

            {LANGUAGE_CONTEXT}

            Create a practical legal action plan for:

            {situation}

            Include:

            1. Immediate Actions
            2. Documents and Evidence Required
            3. Authorities to Contact
            4. Step-by-Step Procedure
            5. Important Precautions
            6. When Professional Legal Help Is Needed
            7. Official Sources

            Do not invent contact details or legal procedures.
            """

            with st.spinner("Preparing your action plan..."):

                result = ask_gemini(prompt)

            st.subheader("Your Action Plan")

            st.markdown(result)

        else:

            st.warning("Please describe your situation.")


# =====================================================
# 14. DOCUMENT GENERATOR
# =====================================================

elif page == "Document Generator":

    st.title("📄 Legal Document Generator")

    st.write(
        "Create a draft complaint letter or legal communication."
    )

    document_type = st.selectbox(
        "Choose Document Type",
        [
            "Consumer Complaint",
            "Salary Not Paid Complaint",
            "Rental Deposit Refund Letter",
            "General Complaint Letter"
        ]
    )

    details = st.text_area(
        "Enter the relevant details",
        height=180,
        placeholder="Enter names, dates, incident details and requested resolution..."
    )

    if st.button("✨ Generate Document"):

        if details.strip():

            prompt = f"""
            {SYSTEM_CONTEXT}

            {LANGUAGE_CONTEXT}

            Generate a formal draft document for India.

            Document Type:
            {document_type}

            Details:
            {details}

            Requirements:

            1. Use a professional format.
            2. Include an appropriate heading.
            3. Include a subject.
            4. Explain the incident clearly.
            5. Include the requested resolution.
            6. Use placeholders for missing personal information.
            7. Never invent facts or legal provisions.
            8. Mark it as a draft requiring user review.
            """

            with st.spinner("Generating your document..."):

                result = ask_gemini(prompt)

            st.session_state.generated_document = result

    if "generated_document" in st.session_state:

        st.markdown("---")

        st.subheader("Your Generated Document")

        st.text_area(
            "Review your document",
            value=st.session_state.generated_document,
            height=350
        )

        pdf_file = create_pdf(
            st.session_state.generated_document
        )

        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_file,
            file_name="Just4All_Legal_Document.pdf",
            mime="application/pdf"
        )


# =====================================================
# 15. KNOW YOUR RIGHTS
# =====================================================

elif page == "Know Your Rights":

    st.title("⚖️ Know Your Rights")

    st.write(
        "Knowledge of your rights is the first step towards justice."
    )

    category = st.selectbox(
        "Choose a legal category",
        [
            "Consumer Rights",
            "Women's Rights",
            "Cyber Safety and Rights",
            "Employment Rights",
            "Tenant Rights",
            "Student Rights"
        ]
    )

    if st.button("✨ Explore My Rights"):

        prompt = f"""
        {SYSTEM_CONTEXT}

        {LANGUAGE_CONTEXT}

        Explain the legal rights of Indian citizens related to:

        {category}

        Include:

        1. Basic Rights
        2. Relevant Indian Laws
        3. Important Legal Protections
        4. Real-Life Examples
        5. Where to Seek Help
        6. Official Government Sources

        Use simple language.
        Do not invent legal provisions.
        """

        with st.spinner("Exploring your rights..."):

            result = ask_gemini(prompt)

        st.subheader("Your Rights Explained")

        st.markdown(result)


# =====================================================
# 16. FOOTER
# =====================================================

st.markdown("---")

footer1, footer2 = st.columns(2)

with footer1:

    render_html("""
        **⚖️ Just4All**

        Justice for Everyone. Rights Within Reach.
        """
    )

with footer2:

    st.caption(
        "AI-powered legal information platform | India"
    )

st.markdown(
    """
    <div class="disclaimer">
        <b>Disclaimer:</b>
        Just4All provides general legal information and educational
        guidance. AI-generated information may contain errors.
        Verify important legal information through official sources
        and consult a qualified lawyer when necessary.
    </div>
    """)