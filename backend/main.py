from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.rag.pipeline import RAGEngine


app = FastAPI(
    title="StreamFuse API",
    description="Streaming Live RAG backend",
    version="1.0"
)


# Allows the frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


print("Starting StreamFuse RAG engine...")

engine = RAGEngine(
    "data/corpus"
)


class StreamRequest(BaseModel):
    session_id: str
    text: str


@app.get("/")
def root():
    return {
        "project": "StreamFuse",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "engine": "ready"
    }


@app.post("/stream")
def stream(request: StreamRequest):

    result = engine.process(
        session_id=request.session_id,
        text=request.text
    )

    return result