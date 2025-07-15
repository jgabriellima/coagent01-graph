## Prompt: Engenharia de Estado (State Engineering)

Para cada state model (classe de estado) da solução, produza uma documentação detalhada seguindo as diretrizes abaixo:

- Liste cada campo da classe.
- Para cada campo, preencha obrigatoriamente:
    - **PROPÓSITO:** Descreva o motivo da existência do campo e sua importância no workflow.
    - **ONDE É SETADO:** Indique em qual nó do grafo, função, agente ou etapa o campo recebe valor (ex: “setado em document_ingestion_node após storage”).
    - **ONDE É USADO:** Especifique onde esse campo é consumido/lido ou influencia decisões do workflow.
    - **INTERAÇÕES/DEPENDÊNCIAS:** Relacione dependências, campos influenciados ou que influenciam o valor deste campo.
    - **IMPACTO:** Explique o que acontece se o campo estiver ausente, incorreto ou fora do padrão esperado.
    - **EXEMPLO DE VALOR:** Forneça exemplos reais ou típicos de valor.
- Inclua bloco de documentação inline (ou tabela), preferencialmente ao lado da definição do campo.
- Sempre que possível, adicione diagramas (Mermaid/UML) ilustrando como o campo transita pelo workflow.
