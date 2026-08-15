# 🤖 RAG AI Knowledge Assistant

An AI-powered **Retrieval-Augmented Generation (RAG)** application that allows users to upload documents and interact with them using natural-language questions.

The application combines document retrieval with a Large Language Model to provide answers based on the user's uploaded knowledge base.

---

## 🚀 Live Application

### Frontend
The frontend is deployed as a Streamlit application.

🔗 https://ai-knowledge-assistant-5603.streamlit.app/

### Backend API
🔗 https://ai-knowledge-assistant-1-po9j.onrender.com

### API Documentation
🔗 https://ai-knowledge-assistant-1-po9j.onrender.com/docs

---

## ✨ Features

- 🔐 User Registration and Login
- 📄 Upload documents
- 🧠 Retrieval-Augmented Generation (RAG)
- 🔎 Semantic document retrieval
- 💬 Ask questions about uploaded documents
- 🤖 AI-generated answers using Groq
- 👤 User-specific document management
- ⚡ FastAPI backend
- 🎨 Streamlit frontend
- 🌐 Cloud deployment
- 🔑 Environment-variable based API configuration

---

## 🏗️ Project Architecture

```text
                 ┌──────────────────────┐
                 │   Streamlit Frontend │
                 │      Web Interface   │
                 └──────────┬───────────┘
                            │
                            │ HTTP Requests
                            ▼
                 ┌──────────────────────┐
                 │    FastAPI Backend   │
                 │    REST API Server   │
                 └──────────┬───────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
        Authentication   Documents      RAG Pipeline
             │              │              │
             │              │              ▼
             │              │        Document Retrieval
             │              │              │
             │              │              ▼
             │              │          Groq LLM
             │              │              │
             └──────────────┴──────────────┘
                            │
                            ▼
                     Generated Answer
