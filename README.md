# 🏥 Healthcare Policy Intelligence Assistant

> AI-powered Healthcare Content Management using Retrieval-Augmented Generation (RAG), Semantic Search, and Rule Extraction.

## Overview

Healthcare organizations rely on thousands of pages of clinical guidelines, billing policies, coding manuals, and payer documentation to make treatment, payment, and operational decisions.

Manually reviewing these documents is time-consuming and prone to inconsistencies.

This project demonstrates a lightweight **Healthcare Policy Intelligence Assistant** capable of:

- 📄 Understanding healthcare policy documents
- 💬 Answering policy-related questions
- 📋 Extracting structured policy rules
- 🔍 Retrieving relevant evidence from uploaded documents

This application was developed as a **Hackathon Proof of Concept** for the **Cotiviti Generative AI Developer Internship Assessment**.

---

# Problem Statement

Healthcare policies are:

- Frequently updated
- Difficult to search manually
- Written in complex clinical language
- Critical for payment integrity and compliance

Analysts often spend significant time identifying coverage criteria, documentation requirements, exclusions, and coding guidance.

This proof of concept explores how Generative AI can improve healthcare content management by making policy documents easier to search, understand, and operationalize.

---

# Features

## 📄 Policy Question Answering

Upload a healthcare policy PDF and ask natural language questions such as:

- What are the medical necessity criteria?
- Which CPT codes are covered?
- What documentation is required?
- What are the exclusions?

The application retrieves the most relevant sections and generates grounded responses.

---

## 📋 Rule Extraction

Automatically extracts policy statements and converts them into structured draft rules.

Example output:

```
Rule

BMI optimization is required before surgery.

Category

Requirement

Applies To

Patients undergoing elective knee arthroplasty

Evidence

BMI < 35 with documented optimization efforts.
```

---

## 🔍 Evidence Retrieval

Each generated answer includes supporting excerpts retrieved directly from the uploaded document, allowing users to verify AI-generated responses.

---

# System Architecture

```
Healthcare Policy PDF
          │
          ▼
 Document Parsing
 (PyMuPDF)
          │
          ▼
 Text Chunking
          │
          ▼
 TF-IDF Index
          │
          ▼
 Semantic Retrieval
          │
          ▼
 Policy Question Answering
          │
          ▼
 Rule Extraction
```

---

# Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| Streamlit | User Interface |
| PyMuPDF | PDF Parsing |
| scikit-learn | TF-IDF Retrieval |
| Pandas | Data Processing |
| JSON | Structured Rule Export |

---

# Folder Structure

```
healthcare-policy-intelligence/

│
├── app.py
├── requirements.txt
├── README.md
│
├── assets/
│   └── style.css
│
├── uploads/
│
└── src/
    ├── document_io.py
    ├── rag.py
    ├── rule_extractor.py
```

---

# Running the Application

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run Streamlit

```bash
streamlit run app.py
```

---

# Example Workflow

1. Upload a healthcare policy PDF
2. Ask questions about the policy
3. Review AI-generated answers
4. Verify supporting evidence
5. Extract structured policy rules
6. Download extracted rules as JSON

---

# Example Documents

The application has been tested using publicly available healthcare policy documents including:

- Kaiser Permanente Clinical Review Criteria
- UnitedHealthcare Medical Policies

---

# Current Limitations

This project is a proof of concept and intentionally prioritizes simplicity.

Current limitations include:

- Uses TF-IDF retrieval instead of dense vector embeddings
- Rule extraction is heuristic-based
- Limited support for scanned PDFs requiring OCR
- No authentication or enterprise document management

---

# Future Enhancements

Potential improvements include:

- Retrieval-Augmented Generation (RAG) with vector databases (FAISS/ChromaDB)
- LLM-powered policy comparison
- Healthcare Knowledge Graph
- Policy version change detection
- Structured IF–THEN rule generation
- Multi-document reasoning
- Explainable AI with confidence scoring

---

# Why This Project

This prototype demonstrates how Generative AI can support healthcare content management by reducing manual effort, improving policy accessibility, and transforming unstructured healthcare documents into actionable knowledge.

The concepts demonstrated align with modern AI techniques such as:

- Large Language Models (LLMs)
- Retrieval-Augmented Generation (RAG)
- Document Intelligence
- Rule Extraction
- Healthcare Policy Analysis

---

#Deliverables

1-Written Report  : Report.docx
2-POC : app.py 
3- Presentation : Presentation.pptx
4- Video Recording : Recording-> demo.mp4


# Author

**Shubham Patil**

Arizona State University

MS Data Science

---

## License

This repository was created solely as part of a technical assessment and educational demonstration.
