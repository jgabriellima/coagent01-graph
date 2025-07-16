"""
Vector Database Setup Node for RAG Pipeline
Initializes and maintains vector database instances in memory
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from ..utils import llm
from ..models.state import RAGState


class CollectionNamesResponse(BaseModel):
    """Response model for collection names generation"""
    collection_names: Optional[List[str]] = Field(
        default=["global"],
        description="List of collection names for the vector database"
    )


def vector_db_setup_node(state: RAGState) -> RAGState:
    """
    Configura vector database e determina collections baseadas no escopo
    """
    
    # Single LLM call to generate collection names
    instruction = f"""
    Generate collection names for vector database based on scope:
    
    Vector DB Type: {state.vector_db_type}
    Document Scope: {state.document_scope}
    Target Databases: {str(state.target_databases)}
    
    Return list of collection names following naming patterns for the scope.
    if the scope is "global", return a collection_names list with a single element "global"
    """
    
    response: CollectionNamesResponse = llm(
        instruction,
        CollectionNamesResponse,
        vector_db_type=state.vector_db_type,
        document_scope=state.document_scope,
        target_databases=state.target_databases,
    )
    
    if not response.collection_names:
        response.collection_names = ["global"]
    
    return state.copy(collection_names=response.collection_names) 