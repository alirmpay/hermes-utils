import os
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import torch

MODEL_ID = os.environ.get("MODEL_ID", "sentence-transformers/all-MiniLM-L6-v2")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer(MODEL_ID, device=device)

app = FastAPI()

class EmbedRequest(BaseModel):
    inputs: str | list[str]

class OpenAIEmbedRequest(BaseModel):
    input: str | list[str]
    model: str | None = None

@app.get("/health")
def health():
    return {"status": "ok", "device": device}

@app.post("/embed")
def embed(req: EmbedRequest):
    texts = [req.inputs] if isinstance(req.inputs, str) else req.inputs
    vectors = model.encode(texts, normalize_embeddings=True).tolist()
    return vectors

@app.post("/v1/embeddings")
def openai_embed(req: OpenAIEmbedRequest):
    texts = [req.input] if isinstance(req.input, str) else req.input
    vectors = model.encode(texts, normalize_embeddings=True).tolist()
    return {
        "object": "list",
        "data": [
            {"object": "embedding", "index": i, "embedding": v}
            for i, v in enumerate(vectors)
        ],
        "model": MODEL_ID,
    }
