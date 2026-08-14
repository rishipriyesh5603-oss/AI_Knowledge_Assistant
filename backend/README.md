# FastAPI addition for the existing AI-RAG project

This folder adds FastAPI without replacing the existing Streamlit UI.

## Existing files stay unchanged

```text
AI-RAG/
├── app.py
├── auth.py
├── rag.py
├── users.db
├── chroma_db/
└── backend/
    ├── __init__.py
    ├── main.py
    ├── requirements.txt
    └── README.md
```

## 1. Install FastAPI

Open CMD/PowerShell in the project root:

```bash
cd C:\Users\RISHI\Desktop\AI-RAG
pip install -r backend\requirements.txt
```

Your existing `rag.py` dependencies should already be installed because the current Streamlit application is working.

## 2. Start FastAPI

Run this from the PROJECT ROOT:

```bash
uvicorn backend.main:app --reload --port 8000
```

Do not `cd backend` for this command.

## 3. Open the API

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## 4. Keep Streamlit running

In another terminal:

```bash
cd C:\Users\RISHI\Desktop\AI-RAG
python -m streamlit run app.py
```

The current UI remains on:

```text
http://localhost:8501
```

## Important

Do NOT change `app.py` yet.

Do NOT create a second `users.db`.

Do NOT create a second `chroma_db`.

FastAPI imports and reuses the existing `auth.py` and `rag.py`, so it works alongside the current application.

## API endpoints

```text
GET    /
GET    /health

POST   /auth/register
POST   /auth/login
GET    /auth/users/{user_id}

POST   /documents/upload/{user_id}
GET    /documents/{user_id}
DELETE /documents/{user_id}

POST   /chat
```

The `/docs` Swagger page can be used to test all endpoints before connecting Streamlit to FastAPI.
