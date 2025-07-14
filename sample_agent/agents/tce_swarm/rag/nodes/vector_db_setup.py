"""
Vector Database Setup Node for TCE-PA RAG Pipeline
Initializes and maintains vector database instances in memory
"""

from ..utils import llm
from ..models.state import TCE_RAG_State
import time

def vector_db_setup_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """
    Configura e mantém instâncias de vector database em memória:
    - Inicializa connections para diferentes tipos de VectorDB
    - Carrega embeddings model uma única vez
    - Cria/acessa collections baseadas no escopo
    - Otimiza performance com cache em memória
    """
    
    # Configuração do vector database baseado no tipo
    vector_db_configs = {
        "chroma": "ChromaVectorDB",
        "pinecone": "PineconeVectorDB",
        "weaviate": "WeaviateVectorDB",
        "faiss": "FAISSVectorDB"
    }
    
    # Simula inicialização de instância se não existir
    if state.vector_db_type not in state.vector_db_instances:
        instruction = f"""
        Simule a inicialização de uma instância de vector database:
        
        Tipo: {state.vector_db_type}
        Embedding Model: {state.embedding_model}
        
        Retorne configurações realísticas de inicialização incluindo:
        - Status da conexão
        - Configurações de embedding
        - Diretório de persistência
        - Estatísticas de performance
        """
        
        db_instance = llm(instruction, None, 
                         vector_db_type=state.vector_db_type,
                         embedding_model=state.embedding_model)
        
        # Adiciona instância simulada ao estado
        state.vector_db_instances[state.vector_db_type] = {
            "instance": db_instance,
            "initialized_at": time.time(),
            "status": "active"
        }
    
    # Determina collections baseadas no escopo
    collection_names = []
    if state.document_scope == "global":
        collection_names = [f"tce_{db}" for db in state.target_databases]
    elif state.document_scope == "user_specific":
        collection_names = [f"tce_{db}_{state.user_id}" for db in state.target_databases]
    elif state.document_scope == "session_specific":
        collection_names = [f"tce_{db}_{state.session_id}" for db in state.target_databases]
    
    return state.copy(collection_names=collection_names) 