from __future__ import annotations

import streamlit as st

from src.assistant import ask_ollama


st.set_page_config(
    page_title="Company Knowledge Assistant",
    page_icon="📚",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1100px;
        padding-top: 2.5rem;
    }

    .hero {
        padding: 2rem;
        border: 1px solid #d7e3df;
        border-radius: 18px;
        background:
            linear-gradient(135deg, #eff8f5 0%, #ffffff 70%);
        margin-bottom: 1.5rem;
    }

    .hero-label {
        color: #137b70;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .hero h1 {
        color: #0f2a32;
        margin: 0.45rem 0 0.7rem;
    }

    .hero p {
        color: #52656b;
        font-size: 1.05rem;
        line-height: 1.7;
        max-width: 760px;
    }

    .status {
        display: inline-block;
        padding: 0.4rem 0.75rem;
        border-radius: 999px;
        color: #246a51;
        background: #e9f3ed;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .safety-note {
        border-left: 4px solid #137b70;
        padding: 0.8rem 1rem;
        background: #f6faf8;
        color: #445b61;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <div class="hero-label">Hicks Analytics · Portfolio Project</div>
        <h1>Company Knowledge Assistant</h1>
        <p>
            Ask questions across fictional company policies. The assistant
            retrieves relevant evidence, answers with citations, and refuses
            questions the available documents cannot support.
        </p>
        <span class="status">● Local AI · Ollama</span>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("How it works")
    st.markdown(
        """
        1. **Retrieve** relevant passages  
        2. **Filter** weak matches  
        3. **Apply** structured business rules  
        4. **Generate** a grounded answer  
        5. **Cite** the supporting sources
        """
    )

    st.divider()
    st.subheader("Knowledge sources")
    st.markdown(
        """
        - Employee handbook
        - Travel and expense policy
        - Vendor management standard
        - Information security policy
        - Accounts payable procedures
        """
    )

    st.divider()
    st.caption(
        "All company names, policies, amounts, and scenarios in this "
        "demonstration are fictional."
    )

st.subheader("Ask a company-policy question")

example = st.selectbox(
    "Try an example",
    [
        "",
        "How much PTO do full-time employees receive?",
        "When must employees submit expense reports after a trip?",
        "Who must approve a $12,000 invoice?",
        "Can confidential information be pasted into a public AI tool?",
        "What is the company's parental leave policy?",
    ],
)

question = st.text_input(
    "Question",
    value=example,
    placeholder="Ask about PTO, expenses, vendors, security, or invoices...",
)

ask_clicked = st.button(
    "Ask the knowledge assistant",
    type="primary",
    use_container_width=True,
)

if ask_clicked:
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        with st.spinner("Retrieving evidence and checking the answer..."):
            try:
                answer = ask_ollama(question.strip())
            except Exception as exc:
                st.error(str(exc))
            else:
                st.subheader("Grounded answer")
                st.markdown(answer)

st.markdown(
    """
    <div class="safety-note">
        <strong>Human review matters.</strong>
        This assistant supports policy discovery and explanation. Confirm
        consequential HR, financial, security, and compliance decisions with
        the responsible policy owner.
    </div>
    """,
    unsafe_allow_html=True,
)