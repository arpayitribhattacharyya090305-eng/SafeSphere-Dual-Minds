from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.services.rag_service import RAGService
from typing import List, Dict, Any

router = APIRouter(prefix="/medical", tags=["Medical RAG Advisor"])

class MedicalQueryRequest(BaseModel):
    query: str
    limit: int = 2

@router.post("/query", response_model=List[Dict[str, Any]])
def query_medical_guidelines(request: MedicalQueryRequest):
    """
    Query the ChromaDB RAG knowledge base for disaster medical first-aid guidelines.
    Falls back to Jaccard similarity search when ChromaDB is unavailable.
    """
    return RAGService.query(request.query, request.limit)
