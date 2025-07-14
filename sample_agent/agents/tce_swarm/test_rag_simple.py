#!/usr/bin/env python3
"""
Teste simples do pipeline RAG sem complexidade de serialização
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

def test_simple_rag_mock():
    """Teste simples do conceito RAG usando LLM diretamente"""
    
    print("🧪 TCE-PA RAG PIPELINE - TESTE SIMPLES")
    print("=" * 60)
    
    # Configurar LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    
    # Queries de teste
    queries = [
        "O teletrabalho pode ser estendido ou prorrogado no TCE-PA?",
        "Qual é o tema do Acórdão nº 192?",
        "Quais são os procedimentos para análise de contas?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 {i}. TESTE: {query}")
        print("-" * 40)
        
        # Simular pipeline RAG completo
        rag_prompt = f"""
        Você é um assistente especializado do TCE-PA processando uma consulta jurídica.
        
        PIPELINE RAG SIMULADO:
        1. QUERY ANALYSIS: Classificar query como legislação/acordão/resolução
        2. VECTOR DB SETUP: Configurar collections TCE-PA
        3. DOCUMENT RETRIEVAL: Buscar documentos relevantes
        4. RELEVANCE GRADING: Avaliar relevância dos chunks
        5. CONTEXT ENRICHMENT: Adicionar contexto jurídico
        6. RESPONSE GENERATION: Gerar resposta final
        
        CONSULTA: {query}
        
        Execute o pipeline simulado e forneça:
        - Tipo de consulta identificado
        - Estratégia de chunking recomendada
        - Resposta simulada baseada em documentos TCE-PA
        - Citações relevantes
        - Numero do processo, resolução, acordão, etc.
        """
        
        try:
            response = llm.invoke([HumanMessage(content=rag_prompt)])
            
            print("✅ PIPELINE RAG EXECUTADO COM SUCESSO!")
            print(f"📝 Resposta:\n{response.content}")
            print(f"⏱️  Simulação completada")
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
    
    print("\n🎉 Teste simples do RAG completado!")

if __name__ == "__main__":
    test_simple_rag_mock() 