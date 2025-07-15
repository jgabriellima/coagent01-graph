## Prompt: Engenharia de Handoff

Para cada ponto de handoff (transferência de contexto/controle entre agentes ou entre agente e humano):

- Especifique:
    - Origem e destino do handoff (quais agentes/workflows estão envolvidos)
    - Gatilhos e condições que disparam a transferência
    - Quais dados/contextos são transferidos e como (estrutura, transformação, serialização)
    - Mecanismo técnico do handoff (evento, chamada direta, callback, mensagem, etc.)
    - Design pattern adotado (ex: Chain of Responsibility, Event-Driven)
    - Validações, possíveis erros, rollback e tratamento de exceções
    - Estratégias de rastreabilidade (logging, tags, traces)
- Inclua diagrama ou tabela ilustrando o fluxo do handoff, com ênfase em pontos críticos e na continuidade do workflow após a transferência.
- Explique o racional do design do handoff, os ganhos de auditabilidade e robustez, e possíveis pontos de extensão futura.
