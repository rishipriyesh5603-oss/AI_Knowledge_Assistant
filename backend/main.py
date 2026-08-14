"""
FastAPI backend added alongside the existing Streamlit RAG app.

IMPORTANT:
- This file does NOT replace app.py, auth.py, or rag.py.
- Run Uvicorn from the AI-RAG project root so the existing users.db
  and chroma_db are reused by auth.py and rag.py.
"""

from pathlib import Path
import os
import sys
import shutil
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Make the existing project files importable when this file is launched
# through: uvicorn backend.main:app --reload --port 8000
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from auth import register_user, login_user, get_user
from rag import (
    process_pdf,
    search_documents,
    generate_answer,
    get_user_chunk_count,
    get_user_sources,
    delete_user_documents,
)


app = FastAPI(
    title="RAG AI Knowledge Assistant API",
    description=(
        "API layer added alongside the existing Streamlit RAG application. "
        "It reuses the existing authentication, ChromaDB, embeddings and Ollama RAG code."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=256)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=256)


class QuestionRequest(BaseModel):
    user_id: int
    question: str = Field(min_length=1, max_length=10000)


def _safe_user(user):
    """Return only the public user fields used by the frontend."""
    if not user:
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
    }


@app.get("/")
def root():
    return {
        "status": "online",
        "message": "RAG AI Assistant API",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "rag-api",
    }


# ------------------------------------------------------------------
# Authentication
# ------------------------------------------------------------------

@app.post("/auth/register")
def register(request: RegisterRequest):
    success, message = register_user(
        request.username.strip(),
        request.email.strip().lower(),
        request.password,
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail=message,
        )

    return {
        "success": True,
        "message": message,
    }


@app.post("/auth/login")
def login(request: LoginRequest):
    user = login_user(
        request.username.strip(),
        request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username/email or password.",
        )

    return {
        "success": True,
        "user": _safe_user(user),
    }


@app.get("/auth/users/{user_id}")
def current_user(user_id: int):
    user = get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return {
        "success": True,
        "user": _safe_user(user),
    }


# ------------------------------------------------------------------
# Documents
# ------------------------------------------------------------------

@app.post("/documents/upload/{user_id}")
async def upload_document(
    user_id: int,
    file: UploadFile = File(...),
):
    user = get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    filename = file.filename or "document.pdf"

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:
            temp_path = temp_file.name

            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                temp_file.write(chunk)

        chunk_count = process_pdf(
            temp_path,
            user_id,
        )

        if chunk_count == 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    "The PDF contained no extractable text. "
                    "If it is scanned/image-only, OCR is required."
                ),
            )

        return {
            "success": True,
            "filename": filename,
            "chunks": chunk_count,
            "message": "Document indexed successfully.",
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {exc}",
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        await file.close()


@app.get("/documents/{user_id}")
def documents(user_id: int):
    user = get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    sources = get_user_sources(user_id)
    chunk_count = get_user_chunk_count(user_id)

    return {
        "success": True,
        "documents": sources,
        "document_count": len(sources),
        "chunk_count": chunk_count,
    }


@app.delete("/documents/{user_id}")
def delete_documents(user_id: int):
    user = get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    deleted = delete_user_documents(user_id)

    return {
        "success": True,
        "deleted_chunks": deleted,
    }


# ------------------------------------------------------------------
# RAG chat
# ------------------------------------------------------------------

@app.post("/chat")
def chat(request: QuestionRequest):
    user = get_user(request.user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    chunk_count = get_user_chunk_count(request.user_id)

    if chunk_count == 0:
        return {
            "success": True,
            "answer": (
                "Your knowledge base is empty. "
                "Please upload and process a PDF first."
            ),
            "sources": [],
        }

    try:
        retrieved_documents = search_documents(
            question,
            request.user_id,
        )

        answer = generate_answer(
            question,
            retrieved_documents,
        )

        sources = [
            {
                "source": item.get("source", "Unknown"),
                "page": item.get("page", "Unknown"),
            }
            for item in retrieved_documents
        ]

        return {
            "success": True,
            "answer": answer,
            "sources": sources,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"RAG request failed: {exc}",
        )
