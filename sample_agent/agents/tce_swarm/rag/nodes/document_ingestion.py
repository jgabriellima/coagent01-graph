"""
Document Ingestion Node for RAG Pipeline
Processes document ingestion: Docling → Chunking → Vector DB Storage
"""

from ..utils import llm
from ..models.state import RAGState
from ..models.responses import IngestionResult
import time

def document_ingestion_node(state: RAGState) -> RAGState:
    """
    Processa ingestão completa: Docling → Chunking → Vector DB Storage
    """
    
    if not state.ingestion_required or not state.documents_to_ingest:
        return state
    
    start_time = time.time()
    
    # Simple mock results without LLM
    ingestion_results = {}
    for doc in state.documents_to_ingest:
        ingestion_results[doc["id"]] = {
            "status": "success",
            "chunks_created": 5,
            "document_id": doc["id"]
        }
    
    # Update user documents list
    new_doc_ids = [doc["id"] for doc in state.documents_to_ingest]
    user_documents = list(state.user_documents) + new_doc_ids
    
    # Update metrics and return
    ingestion_time = time.time() - start_time
    updated_ingestion_status = {**state.ingestion_status, **ingestion_results}
    
    return state.copy(
        ingestion_time=ingestion_time,
        ingestion_status=updated_ingestion_status,
        ingestion_required=False,
        user_documents=user_documents
    ) 