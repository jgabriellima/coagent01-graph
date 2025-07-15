# INSTRUÇÃO PARA GERAÇÃO DE DOCUMENTAÇÃO TÉCNICA INTEGRADA — ARQUITETURA MULTI-AGENTE + RAG (DAS + PI)

## Objetivo
Gerar um **documento técnico integrado** para o projeto Chat Contas — TCE-PA, unindo Arquitetura da Solução (DAS) e Plano de Implementação (PI), para sistemas multi-agente baseados em LangGraph e pipeline RAG.  
O documento deve ser **técnico, detalhado, rastreável e autoexplicativo**, eliminando ambiguidades, facilitando onboarding, manutenção e auditoria.

---

## Diretrizes de Engenharia Aplicadas

Cada uma das engenharias a seguir deve ser abordada em seção própria, explicitando:
- **Definição e propósito no contexto do sistema**
- **Como é aplicada concretamente no projeto**
- **Quais artefatos, padrões e exemplos devem ser documentados**
- **Como garantir que o documento seja referência completa sobre o tema**

### 1. **Engenharia de Estado (State Engineering)**
- **Como preencher:**  
  - Para cada campo dos state models, documente:
    - PROPÓSITO, ONDE É SETADO, ONDE É USADO, INTERAÇÕES/DEPENDÊNCIAS, IMPACTO, EXEMPLO DE VALOR
    - Use blocos de documentação inline e/ou tabelas
    - Inclua diagramas mostrando transição e uso dos campos no workflow
  - **Objetivo:** Garantir que qualquer pessoa compreenda a trajetória e relevância de cada informação ao longo do grafo/fluxo.

### 2. **Engenharia de Fluxo (Flow Engineering)**
- **Como preencher:**  
  - Para cada workflow principal e subfluxo (ex: pipeline RAG, handoff, HITL):
    - Descreva e ilustre toda a sequência de etapas, pontos de decisão, ramificações, breakpoints, fluxos de erro
    - Inclua diagramas de sequência, fluxogramas e explicações textuais
    - Mostre explicitamente o caminho dos dados, triggers e eventos relevantes
  - **Objetivo:** Tornar rastreável e auditável o comportamento do sistema, inclusive em situações alternativas (erros, fallback, intervenção humana).

### 3. **Engenharia de Prompt (Prompt Engineering)**
- **Como preencher:**  
  - Liste todos os prompts templates usados, por agente/contexto
  - Para cada template:
    - Explique objetivo, parâmetros, estrutura, versionamento
    - Inclua nossos usos reais (ou exemplos ralisticos) (Jinja2, etc.) e estratégias para customização, fallback
    - Descreva integração com o state/contexto do sistema
  - **Objetivo:** Garantir transparência, controle de qualidade e fácil evolução dos prompts LLM.

### 4. **Engenharia de Tooling**
- **Como preencher:**  
  - Liste e documente todas as tools/ferramentas utilizadas por agentes:
    - Nome, assinatura, objetivo, inputs/outputs, exemplos de uso, contratos/tipos, agentes habilitados
    - Descreva design patterns associados (ex: Command, Adapter)
    - Mostre guidelines para extensão, testes, versionamento e logging de ferramentas
  - **Objetivo:** Padronizar, facilitar integração/extensão e garantir segurança e rastreabilidade das funções invocáveis por agentes.

### 5. **Engenharia de Handoff**
- **Como preencher:**  
  - Para cada ponto de handoff (transferência de contexto/responsabilidade entre agentes ou entre agente e humano):
    - Documente origem/destino, triggers, dados transferidos, transformações, mecanismos técnicos (ex: eventos, chamadas diretas), design patterns aplicados
    - Inclua diagramas de sequência ou tabelas ilustrando o processo e possíveis falhas
    - Destaque estratégias para atomicidade, rollback e rastreabilidade
  - **Objetivo:** Garantir clareza, auditabilidade e robustez na transferência de controle/contexto no sistema multi-agente.

---

## Organização Sugerida do Documento

1. **Resumo Executivo**
2. **Contexto e Motivação**
3. **Visão Geral da Arquitetura Multi-Agente**
4. **Diretrizes de Engenharia Aplicadas**
    - Engenharia de Estado
    - Engenharia de Fluxo
    - Engenharia de Prompt
    - Engenharia de Tooling
    - Engenharia de Handoff
5. **Descrição Detalhada dos Agentes, Tools e HandOffs**
    - Para cada agente: responsabilidade, ciclo de vida, design pattern, fluxos, observações
    - Para cada tool: contrato, inputs/outputs, exemplos, uso prático
    - Para cada handoff: origem, destino, triggers, fluxo, validações
6. **Prompt Templating e Hooks**
7. **Pipeline RAG**
8. **Fluxos Reais de Interação**
9. **Plano de Implementação (Execução)**
10. **Glossário Técnico e Referências**
11. **Anexos**

---

## Princípios para Escrita e Organização

- Clareza absoluta e detalhamento equilibrado: tudo relevante deve estar presente, mas sem excesso de obviedades.
- Exemplos práticos, diagramas e referências cruzadas em todas as seções técnicas.
- Padrão consistente de títulos, bullets, tabelas, blocos de código.
- Glossário acessível para todos os termos e siglas.

---

## Resumo para o assistente

> O documento final deve ser uma referência total e viva, abrangendo arquitetura, fluxo, estados, prompts, tools e handoffs do sistema multi-agente + RAG do TCE-PA.  
> Cada seção de engenharia aplicada deve ser preenchida com exemplos, padrões, artefatos e guidelines práticos, tornando o sistema rastreável, auditável, extensível e fácil de operar/evoluir.
> Os fluxos devem ser implementados em mermaid, devem ser autoexplicativos, didaticos e que representem a implemntação real.
> Publico alvo: arquitetos, desenvolvedores de alto nivel, analistas especialistas em worfklows de IA
---
