"""
Document Ingestion Node for TCE-PA RAG Pipeline
Processes document ingestion: Docling → Chunking → Vector DB Storage
"""

from ..utils import llm, mock_document_processing, mock_chunking
from ..models.state import TCE_RAG_State
from ..models.responses import IngestionResult
import time

def document_ingestion_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """
    Processa ingestão completa: Docling → Chunking → Vector DB Storage
    """
    
    if not state.needs_ingestion or not state.documents_to_ingest:
        return state
    
    start_time = time.time()
    
    ingestion_results = {}
    
    for doc_info in state.documents_to_ingest:
        doc_id = doc_info["id"]
        file_path = doc_info["file_path"]
        doc_type = doc_info.get("type", "expediente")
        doc_metadata = doc_info.get("metadata", {})
        
        try:
            # ETAPA 1: Document Reading & Parsing com Docling
            parsing_result = mock_document_processing(file_path, doc_type)
            
            if not parsing_result.success:
                raise Exception(f"Document parsing failed: {parsing_result.method}")
            
            # ETAPA 2: Aplicar chunking com estratégia selecionada
            chunks = mock_chunking(
                parsing_result.raw_markdown,
                state.selected_chunker,
                state.chunking_metadata
            )
            
            # ETAPA 3: Enriquecer metadados
            enriched_metadata = {
                **doc_metadata,
                **parsing_result.metadata,
                "user_id": state.user_id,
                "session_id": state.session_id,
                "document_scope": state.document_scope,
                "ingestion_timestamp": time.time(),
                "doc_id": doc_id,
                "structured_content": parsing_result.structured_content
            }
            
            # ETAPA 4: Simular storage no vector database
            instruction = f"""
            Simule o armazenamento de chunks no vector database:
            
            Chunks: {chunks.total_chunks} chunks gerados
            Collection: {state.collection_names}
            User ID: {state.user_id}
            Document Scope: {state.document_scope}
            
            Retorne status de ingestão realístico.
            """
            
            storage_result = llm(instruction, IngestionResult,
                               chunks=chunks.chunks,
                               collection=state.collection_names,
                               user_id=state.user_id,
                               document_id=doc_id)
            
            # Atualizar documentos do usuário
            state.user_documents.append(doc_id)
            ingestion_results[doc_id] = storage_result.model_dump()
            
        except Exception as e:
            ingestion_results[doc_id] = {
                "status": "error",
                "error": str(e),
                "document_id": doc_id
            }
    
    # Atualizar estado
    state.ingestion_time = time.time() - start_time
    state.ingestion_status.update(ingestion_results)
    state.needs_ingestion = False
    
    return state 