# 🧠 Financial Analyst Copilot (AI-Powered RAG System)

An intelligent **Retrieval-Augmented Generation (RAG)** system that analyzes **SEC filings (10-K / 10-Q)** and generates contextual financial insights.  
Built with **LangChain, FAISS, GPT-4o, Sentence Transformers, and Streamlit**.

---

## 🚀 Day 1 — Environment Setup & ETL Pipeline

### ✅ Completed Tasks

#### 1. Environment Setup
- Installed **Python 3.14** and created an isolated virtual environment (`venv`).
- Installed required dependencies:
  ```bash
  pip install langchain faiss-cpu sentence-transformers streamlit requests beautifulsoup4 pandas

financial-analyst-copilot/
│
├── src/                 # Source code (Python scripts)
│   └── etl_sec_ingestor.py
│
├── data/
│   ├── raw/             # Raw HTML SEC filings
│   └── processed/       # Cleaned text data
│
├── notes/               # Documentation & PDFs
├── venv/                # Virtual environment
└── requirements.txt     # Dependency list

