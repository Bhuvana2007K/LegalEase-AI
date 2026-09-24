from __future__ import annotations

import html
import os
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

REQUEST_TIMEOUT = int(
    os.getenv(
        "REQUEST_TIMEOUT_SECONDS",
        "120",
    )
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 17px;
        margin-bottom: 25px;
    }

    .legal-notice {
        padding: 15px;
        border-radius: 10px;
        background-color: #fff7ed;
        border: 1px solid #fed7aa;
        color: #7c2d12;
        margin-bottom: 20px;
    }

    .document-preview {
        background: #111827;
        color: #f9fafb;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #374151;
        min-height: 300px;
        line-height: 1.7;
        font-family: Georgia, serif;
        white-space: normal;
        overflow-wrap: anywhere;
    }

    .status-card {
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "document_content" not in st.session_state:
    st.session_state.document_content = ""

if "document_type" not in st.session_state:
    st.session_state.document_type = "Freelance Work Contract"


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">AI-Powered Legal Document Generator</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="legal-notice">
        <strong>Important:</strong>
        LegalEase generates draft documents for informational and
        document-preparation purposes. Generated documents should be
        reviewed by a qualified legal professional before signing.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("System Status")

    try:
        health_response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=5,
        )

        if health_response.ok:

            health = health_response.json()

            st.success("Backend Online")

            st.write(
                f"**Model:** `{health.get('model', 'Unknown')}`"
            )

            gemini_configured = health.get(
                "gemini_configured",
                False,
            )

            if gemini_configured:
                st.success("Gemini API configured")
            else:
                st.warning("Gemini API key not configured")

        else:

            st.error("Backend returned an error.")

    except requests.RequestException:

        st.error("Backend Offline")

        st.caption(
            "Start the backend with:\n\n"
            "`uvicorn backend.main:app --reload`"
        )

    st.divider()

    st.header("About")

    st.write(
        """
        LegalEase converts structured user requirements into
        editable legal-document drafts using Google Gemini.
        """
    )

    st.divider()

    st.caption(
        "For production deployment, add authentication, "
        "rate limiting, HTTPS, secure secret storage, logging, "
        "privacy controls, and jurisdiction-specific legal review."
    )


# ============================================================
# INPUT FORM
# ============================================================

st.header("Create Your Legal Document")

with st.form("document_generation_form"):

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # LEFT COLUMN
    # --------------------------------------------------------

    with col1:

        document_type = st.text_input(
            "Document Type",
            value=st.session_state.document_type,
            placeholder="Example: Non-Disclosure Agreement",
        )

        parties = st.text_area(
            "Parties Involved",
            height=130,
            placeholder=(
                "Example:\n"
                "Jane Doe (Disclosing Party)\n"
                "TechNova Inc. (Receiving Party)"
            ),
        )

        effective_date = st.text_input(
            "Effective Date",
            value=date.today().isoformat(),
        )

    # --------------------------------------------------------
    # RIGHT COLUMN
    # --------------------------------------------------------

    with col2:

        terms = st.text_area(
            "Terms & Conditions",
            height=130,
            placeholder=(
                "Example:\n"
                "Confidential information must be protected.\n"
                "Payment is due within 30 days.\n"
                "Either party may terminate with 15 days notice."
            ),
        )

        jurisdiction = st.text_input(
            "Jurisdiction",
            placeholder="Example: India / Tamil Nadu",
        )

        additional_instructions = st.text_area(
            "Additional Instructions",
            height=90,
            placeholder=(
                "Example: Use clear professional language "
                "and include signature blocks."
            ),
        )

    submitted = st.form_submit_button(
        "🚀 Generate Document",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# GENERATE DOCUMENT
# ============================================================

if submitted:

    if not document_type.strip():
        st.error("Please enter a document type.")

    elif not parties.strip():
        st.error("Please enter the parties involved.")

    elif not terms.strip():
        st.error("Please enter the terms and conditions.")

    elif not effective_date.strip():
        st.error("Please enter an effective date.")

    else:

        payload = {
            "document_type": document_type.strip(),
            "parties": parties.strip(),
            "terms": terms.strip(),
            "effective_date": effective_date.strip(),
            "jurisdiction": jurisdiction.strip(),
            "additional_instructions": additional_instructions.strip(),
        }

        with st.spinner(
            "Gemini is drafting your legal document..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=REQUEST_TIMEOUT,
                )

            except requests.RequestException as error:

                st.error(
                    "Unable to connect to the FastAPI backend."
                )

                st.code(str(error))

            else:

                if response.ok:

                    result = response.json()

                    st.session_state.document_content = (
                        result["content"]
                    )

                    st.session_state.document_type = (
                        result["document_type"]
                    )

                    st.success(
                        "Document generated successfully."
                    )

                else:

                    try:
                        error_data = response.json()
                        error_message = error_data.get(
                            "detail",
                            "Unknown backend error.",
                        )
                    except Exception:
                        error_message = response.text

                    st.error(
                        f"Generation failed "
                        f"({response.status_code}): "
                        f"{error_message}"
                    )


# ============================================================
# DOCUMENT EDITOR
# ============================================================

if st.session_state.document_content:

    st.divider()

    st.header("Document Editor")

    st.write(
        "You can edit the generated document before exporting it."
    )

    edited_document = st.text_area(
        "Generated Document",
        value=st.session_state.document_content,
        height=600,
        label_visibility="collapsed",
    )

    st.session_state.document_content = edited_document

    # ========================================================
    # PREVIEW
    # ========================================================

    st.subheader("Preview")

    escaped_document = html.escape(
        st.session_state.document_content
    )

    escaped_document = escaped_document.replace(
        "\n\n",
        "</p><p>",
    )

    escaped_document = escaped_document.replace(
        "\n",
        "<br>",
    )

    preview_html = (
        '<div class="document-preview">'
        f"<p>{escaped_document}</p>"
        "</div>"
    )

    st.markdown(
        preview_html,
        unsafe_allow_html=True,
    )

    # ========================================================
    # DOCUMENT STATISTICS
    # ========================================================

    stat1, stat2, stat3 = st.columns(3)

    with stat1:
        st.metric(
            "Characters",
            len(st.session_state.document_content),
        )

    with stat2:
        word_count = len(
            st.session_state.document_content.split()
        )

        st.metric(
            "Words",
            word_count,
        )

    with stat3:

        line_count = len(
            st.session_state.document_content.splitlines()
        )

        st.metric(
            "Lines",
            line_count,
        )

    # ========================================================
    # EXPORT
    # ========================================================

    st.divider()

    st.header("Download Document")

    export_payload = {
        "document_type": st.session_state.document_type,
        "content": st.session_state.document_content,
    }

    col_txt, col_docx, col_pdf = st.columns(3)

    # --------------------------------------------------------
    # TXT
    # --------------------------------------------------------

    with col_txt:

        try:

            response = requests.post(
                f"{BACKEND_URL}/export/txt",
                json=export_payload,
                timeout=30,
            )

            if response.ok:

                st.download_button(
                    label="📄 Download TXT",
                    data=response.content,
                    file_name="legalease_document.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            else:

                st.error("TXT export failed.")

        except requests.RequestException:

            st.error("Backend unavailable.")

    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    with col_docx:

        try:

            response = requests.post(
                f"{BACKEND_URL}/export/docx",
                json=export_payload,
                timeout=30,
            )

            if response.ok:

                st.download_button(
                    label="📝 Download DOCX",
                    data=response.content,
                    file_name="legalease_document.docx",
                    mime=(
                        "application/"
                        "vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),
                    use_container_width=True,
                )

            else:

                st.error("DOCX export failed.")

        except requests.RequestException:

            st.error("Backend unavailable.")

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    with col_pdf:

        try:

            response = requests.post(
                f"{BACKEND_URL}/export/pdf",
                json=export_payload,
                timeout=30,
            )

            if response.ok:

                st.download_button(
                    label="📕 Download PDF",
                    data=response.content,
                    file_name="legalease_document.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            else:

                st.error("PDF export failed.")

        except requests.RequestException:

            st.error("Backend unavailable.")

else:

    st.info(
        "Fill in the document details above and click "
        "**Generate Document**."
    )