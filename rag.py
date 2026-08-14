import os
import hashlib

from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not configured")

groq_client = Groq(api_key=GROQ_API_KEY)


# =========================================================
# CONFIGURATION
# =========================================================

CHROMA_PATH = "./chroma_db"

COLLECTION_NAME = "rag_documents"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

LLM_MODEL = "llama-3.3-70b-versatile"

CHUNK_SIZE = 800

CHUNK_OVERLAP = 150

TOP_K = 5


# =========================================================
# MODELS
# =========================================================

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={
        "hnsw:space": "cosine"
    }
)


# =========================================================
# PDF EXTRACTION
# =========================================================

def extract_pdf_text(file_path):

    reader = PdfReader(
        file_path
    )

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text()

        if text and text.strip():

            pages.append({
                "page": page_number,
                "text": text.strip()
            })

    return pages


# =========================================================
# CHUNKING
# =========================================================

def create_chunks(
    text,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP
):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(
            words[start:end]
        )

        if chunk.strip():

            chunks.append(chunk)

        start += (
            chunk_size - overlap
        )

    return chunks


# =========================================================
# ID
# =========================================================

def generate_id(text):

    return hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()


# =========================================================
# PROCESS PDF
# =========================================================

def process_pdf(
    file_path,
    user_id
):

    filename = os.path.basename(
        file_path
    )

    pages = extract_pdf_text(
        file_path
    )

    if not pages:
        return 0

    documents = []

    metadatas = []

    ids = []

    for page_data in pages:

        page_number = page_data["page"]

        page_text = page_data["text"]

        chunks = create_chunks(
            page_text
        )

        for chunk_index, chunk in enumerate(
            chunks
        ):

            document_id = generate_id(
                f"{user_id}_{filename}_{page_number}_{chunk_index}_{chunk}"
            )

            documents.append(
                chunk
            )

            metadatas.append({

                "user_id": str(user_id),

                "source": filename,

                "page": page_number,

                "chunk": chunk_index
            })

            ids.append(
                document_id
            )

    if not documents:

        return 0

    embeddings = embedding_model.encode(
        documents,
        normalize_embeddings=True
    ).tolist()

    collection.upsert(

        ids=ids,

        documents=documents,

        embeddings=embeddings,

        metadatas=metadatas
    )

    return len(documents)


# =========================================================
# SEARCH DOCUMENTS
# =========================================================

def search_documents(
    query,
    user_id,
    top_k=TOP_K
):

    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True
    )[0].tolist()

    results = collection.query(

        query_embeddings=[
            query_embedding
        ],

        n_results=top_k,

        where={
            "user_id": str(user_id)
        }
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    combined_results = []

    for document, metadata in zip(
        documents,
        metadatas
    ):

        combined_results.append({

            "text": document,

            "source": metadata.get(
                "source",
                "Unknown"
            ),

            "page": metadata.get(
                "page",
                "Unknown"
            )
        })

    return combined_results


# =========================================================
# GENERATE ANSWER
# =========================================================

def generate_answer(
    question,
    retrieved_documents
):

    if not retrieved_documents:

        return (
            "I could not find relevant information "
            "in your uploaded documents."
        )

    context_parts = []

    for index, item in enumerate(
        retrieved_documents,
        start=1
    ):

        context_parts.append(
            f"""
SOURCE {index}

File: {item['source']}
Page: {item['page']}

Content:

{item['text']}
"""
        )

    context = "\n".join(
        context_parts
    )

    prompt = f"""
You are a professional RAG AI assistant.

Answer the user's question using ONLY
the provided document context.

Rules:

1. Do not invent information.
2. Do not use outside knowledge.
3. If the answer is not present,
   clearly say that you could not find it.
4. Give a concise but useful answer.
5. Use the available source information.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

    response = groq_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful RAG AI assistant. "
                    "Answer the user's question using only the "
                    "provided document context. "
                    "Do not invent information. "
                    "If the answer cannot be found in the provided "
                    "context, clearly say that you could not find "
                    "the answer in the uploaded documents."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_completion_tokens=1024
    )

    answer = response.choices[0].message.content
    


# =========================================================
# USER CHUNK COUNT
# =========================================================

def get_user_chunk_count(
    user_id
):

    results = collection.get(
        where={
            "user_id": str(user_id)
        }
    )

    return len(
        results.get(
            "ids",
            []
        )
    )


# =========================================================
# USER SOURCES
# =========================================================

def get_user_sources(
    user_id
):

    results = collection.get(

        where={
            "user_id": str(user_id)
        }
    )

    metadatas = results.get(
        "metadatas",
        []
    )

    sources = set()

    for metadata in metadatas:

        if metadata:

            source = metadata.get(
                "source"
            )

            if source:
                sources.add(source)

    return sorted(
        sources
    )


# =========================================================
# DELETE USER DATA
# =========================================================

def delete_user_documents(
    user_id
):

    results = collection.get(

        where={
            "user_id": str(user_id)
        }
    )

    ids = results.get(
        "ids",
        []
    )

    if ids:

        collection.delete(
            ids=ids
        )

    return len(ids)

