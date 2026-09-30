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

class StreamChunkRequest(BaseModel):
    session_id: str
    chunk: str
    is_final: bool = False    

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
stream_buffers = {}

@app.post("/stream-chunk")
def stream_chunk(request: StreamChunkRequest):

    session_id = request.session_id
    incoming_chunk = request.chunk.strip()

    current_transcript = stream_buffers.get(
      session_id,
    ""
    ).strip()


# First chunk
    if not current_transcript:
       full_transcript = incoming_chunk


# Frontend sent the entire accumulated transcript
    elif incoming_chunk.startswith(current_transcript):
      full_transcript = incoming_chunk


# Same chunk accidentally sent twice
    elif current_transcript.endswith(incoming_chunk):
      full_transcript = current_transcript


# Normal new incremental chunk
    else:
       full_transcript = (
         current_transcript
         + " "
         + incoming_chunk
        ).strip()
 

    stream_buffers[session_id] = full_transcript
   
    # Run RAG on the transcript accumulated so far
    result = engine.process(
        session_id=session_id,
        text=full_transcript
    )

    response = {
        "session_id": session_id,
        "incoming_chunk": request.chunk,
        "full_transcript": full_transcript,
        "is_final": request.is_final,
        **result
    }

    # Clear transcript buffer after utterance finishes
    if request.is_final:
        stream_buffers.pop(session_id, None)

    return response