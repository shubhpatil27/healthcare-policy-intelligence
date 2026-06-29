from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

from src.document_io import extract_text, split_with_metadata, save_uploaded_file
from src.rag import build_index, answer_question
from src.rule_extractor import extract_rules, rules_to_json, rules_to_text

APP_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Healthcare Policy Intelligence Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Styles ---
style_path = APP_DIR / "assets" / "style.css"
if style_path.exists():
    st.markdown(f"<style>{style_path.read_text()}</style>", unsafe_allow_html=True)

# --- Header ---
st.markdown(
    """
    <div class="hero">
      <span class="badge">Healthcare AI</span>
      <span class="badge">Policy Intelligence</span>
      <span class="badge">RAG</span>
      <h1 class="brand-title">Healthcare Policy Intelligence Assistant</h1>
      <p class="brand-subtitle">
        Upload a healthcare policy PDF, ask grounded questions, and extract draft rules.
        This lightweight demo is built for the Cotiviti hackathon proof-of-concept.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("🏥 Demo Guide")
    st.write("1. Upload a policy PDF or DOCX.")
    st.write("2. Ask a policy question.")
    st.write("3. Extract draft rules for review.")
    st.divider()
    st.caption("Built with Streamlit, TF-IDF retrieval, and rule extraction.")
    st.caption("No API key required for the local demo.")

qa_tab, rules_tab = st.tabs(["📄 Policy Q&A", "📋 Rule Extraction"])


# --- Q&A tab ---
with qa_tab:
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.subheader("Ask questions about a policy")
        qa_upload = st.file_uploader(
            "Upload policy document",
            type=["pdf", "docx"],
            key="qa_upload",
            help="Upload a PDF or DOCX policy document.",
        )
        question = st.text_input(
            "Ask a question",
            placeholder="Does this policy require prior authorization?",
        )
        run_qa = st.button("Get Answer", use_container_width=True)

    with right:
        st.markdown('<div class="softcard">', unsafe_allow_html=True)
        st.markdown("**Example questions**")
        st.write("• Is prior authorization required?")
        st.write("• What CPT codes are covered?")
        st.write("• What are the medical necessity criteria?")
        st.write("• Which exclusions are listed?")
        st.markdown("</div>", unsafe_allow_html=True)

    if qa_upload is not None:
        st.success(f"Uploaded: {qa_upload.name}")
        save_uploaded_file(qa_upload)

    if run_qa:
        if qa_upload is None:
            st.warning("Please upload a document first.")
        elif not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Reading the document and searching relevant sections..."):
                text = extract_text(qa_upload)
                chunks = split_with_metadata(text, qa_upload.name)
                vectorizer, matrix, chunk_objs = build_index(chunks)
                result = answer_question(question, vectorizer, matrix, chunk_objs)

            st.markdown("### Answer")
            st.markdown(f'<div class="result-card">{result.answer}</div>', unsafe_allow_html=True)

            if result.sources:
                st.markdown("### Supporting excerpts")
                for i, (source, score, chunk_text) in enumerate(result.sources, start=1):
                    with st.expander(f"Source {i}: {source} · score {score:.3f}", expanded=(i == 1)):
                        st.write(chunk_text)

                source_df = pd.DataFrame(
                    [{"source": s, "score": round(sc, 3), "excerpt": txt} for s, sc, txt in result.sources]
                )
                st.download_button(
                    "Download sources as CSV",
                    source_df.to_csv(index=False).encode("utf-8"),
                    file_name="qa_sources.csv",
                    mime="text/csv",
                    use_container_width=True,
                )


# --- Rules tab ---
with rules_tab:
    st.subheader("Extract draft rules")
    st.write("Upload one document and extract policy statements that can be reviewed as draft rules.")

    rules_doc = st.file_uploader("Policy document", type=["pdf", "docx"], key="rules_doc")
    extract_clicked = st.button("Extract Rules", use_container_width=True)

    if rules_doc is not None:
        st.success(f"Uploaded: {rules_doc.name}")
        save_uploaded_file(rules_doc)

    if extract_clicked:
        if rules_doc is None:
            st.warning("Upload a document first.")
        else:
            with st.spinner("Extracting policy rules..."):
                text = extract_text(rules_doc)
                rules = extract_rules(text)

            st.markdown("### Draft rules")
            st.code(rules_to_text(rules), language="text")

            st.markdown("### Structured output")
            st.json([r.__dict__ for r in rules[:15]])

            st.download_button(
                "Download rules as JSON",
                rules_to_json(rules).encode("utf-8"),
                file_name="extracted_rules.json",
                mime="application/json",
                use_container_width=True,
            )

st.divider()
st.caption(
    "Hackathon proof of concept: document ingestion, semantic search, and draft rule extraction for healthcare policy content."
)