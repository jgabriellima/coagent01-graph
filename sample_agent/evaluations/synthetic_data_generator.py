#!/usr/bin/env python3
"""
Gerador de Dados Sintéticos para Sistema de Swarm Agents
--------------------------------------------------------

Este módulo gera cenários sintéticos baseados nos agentes disponíveis:
- Alice Agent: Especialista em matemática 
- Bob Agent: Especialista em clima (fala como pirata)
- Main Agent: Coordenador de tarefas
- Swarm Workflow: Sistema completo com handoffs entre agentes

Executa os cenários no sistema real para coletar traces via LangSmith.
Usa LLM para gerar cenários dinâmicos com máxima variabilidade.
"""

import os
import json
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
from langchain_core.tracers import LangChainTracer
from langsmith import Client
import uuid

# Importar os agentes individuais
from sample_agent.agents.swarm.alice_agent import build_alice_agent
from sample_agent.agents.swarm.bob_agent import build_bob_agent
from sample_agent.agents.swarm.main_agent import build_main_agent

# Importar o sistema de swarm completo
from sample_agent.agents.swarm.graph import create_multi_agent_system_swarm_mode


@dataclass
class SyntheticScenario:
    """Representa um cenário sintético para teste"""
    agent_type: str  # "alice", "bob", "main", "swarm"
    scenario_type: str
    user_input: str
    expected_behavior: str
    state_context: Dict[str, Any]
    complexity_level: str  # "simple", "medium", "complex", "edge"
    metadata: Dict[str, Any] = field(default_factory=dict)
    requires_handoff: bool = False  # Se requer handoff entre agentes


@dataclass
class ExecutionResult:
    """Resultado da execução de um cenário"""
    scenario: SyntheticScenario
    trace_id: str
    execution_time: float
    success: bool
    error: Optional[str] = None
    response_messages: List[Any] = field(default_factory=list)
    structured_response: Optional[Dict[str, Any]] = None
    handoffs_performed: List[str] = field(default_factory=list)  # Track agent handoffs


class SyntheticDataGenerator:
    """Gerador de dados sintéticos para o sistema de swarm agents"""
    
    def __init__(
        self,
        model_name: str = "openai:gpt-4o-mini",
        temperature: float = 0.7,
        langsmith_project_name: Optional[str] = None,
        num_scenarios_per_agent: int = 10,
        include_swarm_scenarios: bool = True,
        scenario_generation_mode: str = "hybrid"  # "static", "llm", "hybrid"
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.langsmith_project_name = langsmith_project_name or f"synthetic-data-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.num_scenarios_per_agent = num_scenarios_per_agent
        self.include_swarm_scenarios = include_swarm_scenarios
        self.scenario_generation_mode = scenario_generation_mode
        
        # Configurar LangSmith
        self._setup_langsmith()
        
        # Inicializar modelo
        self.model = init_chat_model(model_name, temperature=temperature)
        
        # Modelo para geração de cenários
        self.scenario_generator_model = init_chat_model(model_name, temperature=0.9)
        
        # Dados base para geração de cenários
        self._load_scenario_templates()
    
    def _setup_langsmith(self):
        """Configura LangSmith para coleta de traces"""
        # Configurar o nome do projeto programaticamente
        os.environ["LANGSMITH_PROJECT"] = self.langsmith_project_name
        
        # Verificar se as variáveis do LangSmith estão definidas
        if not os.getenv("LANGSMITH_API_KEY"):
            print("⚠️  LANGSMITH_API_KEY não encontrada. Traces não serão coletados.")
            return
        
        # Configurar tracing
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        
        try:
            self.langsmith_client = Client()
            print(f"✅ LangSmith configurado - Projeto: {self.langsmith_project_name}")
        except Exception as e:
            print(f"⚠️  Erro ao configurar LangSmith: {e}")
            self.langsmith_client = None
    
    def _load_scenario_templates(self):
        """Carrega templates de cenários para cada agente"""
        
        # Templates base para geração via LLM
        self.scenario_templates = {
            "alice": {
                "identity": "Alice é uma especialista em matemática que resolve cálculos precisos",
                "capabilities": ["cálculos matemáticos", "expressões numéricas", "operações aritméticas"],
                "constraints": ["nunca responde questões não-matemáticas", "sempre usa calculate_math tool"],
                "examples": [
                    "Calcule 2 + 2",
                    "Resolva (3 + 4) * 2",
                    "Quanto é 2 ** 3 + 5 * 2?"
                ]
            },
            "bob": {
                "identity": "Bob é um especialista em clima que fala como pirata",
                "capabilities": ["previsão do tempo", "informações meteorológicas", "clima de locais"],
                "constraints": ["sempre fala como pirata", "nunca responde questões não-meteorológicas", "usa get_weather tool"],
                "examples": [
                    "Qual o tempo em São Paulo?",
                    "Como está o clima no Rio de Janeiro?",
                    "Preciso da previsão para Salvador"
                ]
            },
            "main": {
                "identity": "Main Agent coordena tarefas e redireciona para especialistas",
                "capabilities": ["coordenação", "roteamento de tarefas", "interação com usuário"],
                "constraints": ["roteia matemática para Alice", "roteia clima para Bob", "usa ask_user tool quando necessário"],
                "examples": [
                    "Preciso de ajuda com matemática",
                    "Pode me ajudar com previsão do tempo?",
                    "Quero resolver uma conta e saber o clima"
                ]
            },
            "swarm": {
                "identity": "Sistema completo com handoffs entre Main Agent, Alice e Bob",
                "capabilities": ["tarefas complexas", "múltiplos domínios", "coordenação entre agentes"],
                "constraints": ["handoffs automáticos", "estado compartilhado", "coordenação inteligente"],
                "examples": [
                    "Calcule 10 * 5 e depois me diga o tempo em Brasília",
                    "Preciso resolver (2 + 3) * 4 e saber se chove em Recife",
                    "Quanto é 100 / 4 e qual a temperatura em Manaus?"
                ]
            }
        }
        
        # Templates estáticos (fallback)
        self.static_templates = {
            "alice": [
                "Calcule {expression}",
                "Resolva {expression}",
                "Quanto é {expression}?",
                "Preciso do resultado de {expression}"
            ],
            "bob": [
                "Qual o tempo em {location}?",
                "Como está o clima em {location}?",
                "Preciso da previsão para {location}",
                "Vai chover em {location}?"
            ],
            "main": [
                "Preciso de ajuda com {task}",
                "Pode me ajudar com {task}?",
                "Como faço para {task}?",
                "Quero {task}"
            ],
            "swarm": [
                "Calcule {expression} e me diga o tempo em {location}",
                "Preciso resolver {expression} e saber se chove em {location}",
                "Quanto é {expression} e qual a temperatura em {location}?",
                "Resolva {expression} e depois verifique o clima de {location}"
            ]
        }
        
        # Dados para preenchimento de templates
        self.math_expressions = {
            "simple": ["2 + 2", "10 - 5", "3 * 4", "15 / 3", "2 ** 3"],
            "medium": ["(2 + 3) * 4", "2 ** 3 + 5 * 2", "100 / (2 + 3)", "((10 + 5) / 3) * 2"],
            "complex": ["((2 + 3) * 4) / (5 - 2) + 10", "2 ** (3 + 1) - (5 * 2) / 2", "(100 + 50) / (3 * 5) + 2 ** 4"],
            "edge": ["0 / 1", "1 ** 100", "2 + 2 * 2", "10 / 2 / 2"]
        }
        
        self.locations = {
            "simple": ["São Paulo", "Rio de Janeiro", "Salvador", "Recife", "Brasília"],
            "medium": ["Fernando de Noronha", "Ilha Grande", "Cabo Frio", "Búzios"],
            "complex": ["Gramado", "Campos do Jordão", "Petrópolis", "Tiradentes"],
            "edge": ["Antártica", "Polo Norte", "Sahara", "Everest"]
        }
        
        self.tasks = {
            "simple": ["matemática", "clima", "cálculos", "previsão do tempo"],
            "medium": ["resolver uma conta", "saber o tempo", "calcular expressão", "verificar previsão"],
            "complex": ["tarefas múltiplas", "coordenação", "planejamento", "análise"],
            "edge": ["algo indefinido", "tarefa impossível", "múltiplas coisas", "coordenação complexa"]
        }

    async def generate_llm_scenarios(self, agent_type: str, num_scenarios: int, complexity_level: str) -> List[SyntheticScenario]:
        """Gera cenários usando LLM para máxima variabilidade"""
        scenarios = []
        
        template_info = self.scenario_templates[agent_type]
        
        generation_prompt = f"""
Você é um gerador de cenários de teste para um sistema de IA multi-agente.

AGENTE: {agent_type.upper()}
IDENTIDADE: {template_info['identity']}
CAPACIDADES: {', '.join(template_info['capabilities'])}
RESTRIÇÕES: {', '.join(template_info['constraints'])}

NIVEL DE COMPLEXIDADE: {complexity_level}

EXEMPLOS DE REFERÊNCIA:
{chr(10).join(f"- {ex}" for ex in template_info['examples'])}

INSTRUÇÕES:
1. Gere {num_scenarios} cenários ÚNICOS e VARIADOS
2. Cada cenário deve ser uma pergunta/solicitação que um usuário real faria
3. Variar vocabulário, estrutura e estilo
4. Incluir diferentes tipos de solicitações (direta, indireta, educada, casual)
5. Para complexidade '{complexity_level}', ajustar adequadamente a dificuldade
6. Cenários devem ser REALISTAS e TESTÁVEIS

FORMATO DE RESPOSTA:
Responda APENAS com JSON válido no formato:
{{
    "scenarios": [
        {{
            "user_input": "texto da solicitação do usuário",
            "expected_behavior": "comportamento esperado do agente",
            "context": {{"chave": "valor"}},
            "requires_handoff": false
        }}
    ]
}}

IMPORTANTE: Não inclua explicações, apenas o JSON.
"""
        
        try:
            response = await self.scenario_generator_model.ainvoke([HumanMessage(content=generation_prompt)])
            
            # Parse JSON response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            
            data = json.loads(content)
            
            for i, scenario_data in enumerate(data["scenarios"][:num_scenarios]):
                scenario = SyntheticScenario(
                    agent_type=agent_type,
                    scenario_type=f"llm_generated_{complexity_level}",
                    user_input=scenario_data["user_input"],
                    expected_behavior=scenario_data["expected_behavior"],
                    state_context=scenario_data.get("context", {}),
                    complexity_level=complexity_level,
                    requires_handoff=scenario_data.get("requires_handoff", False),
                    metadata={
                        "generation_method": "llm",
                        "generation_timestamp": datetime.now().isoformat(),
                        "model_used": self.model_name
                    }
                )
                scenarios.append(scenario)
                
        except Exception as e:
            print(f"⚠️  Erro ao gerar cenários via LLM para {agent_type}: {e}")
            # Fallback para geração estática
            scenarios.extend(self.generate_static_scenarios(agent_type, num_scenarios, complexity_level))
        
        return scenarios

    def generate_static_scenarios(self, agent_type: str, num_scenarios: int, complexity_level: str) -> List[SyntheticScenario]:
        """Gera cenários usando templates estáticos (fallback)"""
        scenarios = []
        templates = self.static_templates[agent_type]
        
        for i in range(num_scenarios):
            template = random.choice(templates)
            
            # Preencher template baseado no tipo de agente
            if agent_type == "alice":
                expressions = self.math_expressions[complexity_level]
                user_input = template.format(expression=random.choice(expressions))
                expected_behavior = "Calculate mathematical expression using calculate_math tool"
                
            elif agent_type == "bob":
                locations = self.locations[complexity_level]
                user_input = template.format(location=random.choice(locations))
                expected_behavior = "Get weather information using get_weather tool, respond like a pirate"
                
            elif agent_type == "main":
                tasks = self.tasks[complexity_level]
                user_input = template.format(task=random.choice(tasks))
                expected_behavior = "Coordinate task and handoff to appropriate specialist agent"
                
            elif agent_type == "swarm":
                expressions = self.math_expressions[complexity_level]
                locations = self.locations[complexity_level]
                user_input = template.format(
                    expression=random.choice(expressions),
                    location=random.choice(locations)
                )
                expected_behavior = "Execute multi-agent workflow with handoffs between agents"
            
            scenario = SyntheticScenario(
                agent_type=agent_type,
                scenario_type=f"static_{complexity_level}",
                user_input=user_input,
                expected_behavior=expected_behavior,
                state_context=self._generate_state_context(agent_type),
                complexity_level=complexity_level,
                requires_handoff=(agent_type in ["main", "swarm"]),
                metadata={
                    "generation_method": "static",
                    "generation_timestamp": datetime.now().isoformat(),
                    "template_used": template
                }
            )
            scenarios.append(scenario)
        
        return scenarios

    def _generate_state_context(self, agent_type: str) -> Dict[str, Any]:
        """Gera contexto de estado apropriado para cada tipo de agente"""
        base_context = {
            "thread_mode": "task_only",
            "task_type": agent_type,
            "constraints": []
        }
        
        if agent_type == "alice":
            base_context.update({
                "math_expression": "",
                "math_result": "",
                "constraints": ["Never answer non-math questions", "Always use calculate_math tool"]
            })
        elif agent_type == "bob":
            base_context.update({
                "location": "",
                "weather": "",
                "temperature": 0.0,
                "constraints": ["Speak like a pirate", "Never answer non-weather questions", "Use get_weather tool"]
            })
        elif agent_type in ["main", "swarm"]:
            base_context.update({
                "location": "",
                "weather": "",
                "temperature": 0.0,
                "math_expression": "",
                "math_result": "",
                "constraints": ["Route tasks to appropriate agents", "Use ask_user tool when needed"]
            })
        
        return base_context

    async def generate_scenarios_for_agent(self, agent_type: str, num_scenarios: int = None) -> List[SyntheticScenario]:
        """Gera cenários para um agente específico"""
        num_scenarios = num_scenarios or self.num_scenarios_per_agent
        scenarios = []
        
        # Distribuir cenários por nível de complexidade
        complexity_distribution = {
            "simple": int(num_scenarios * 0.3),
            "medium": int(num_scenarios * 0.4),
            "complex": int(num_scenarios * 0.2),
            "edge": int(num_scenarios * 0.1)
        }
        
        # Ajustar para garantir que soma seja exata
        total_distributed = sum(complexity_distribution.values())
        if total_distributed < num_scenarios:
            complexity_distribution["medium"] += num_scenarios - total_distributed
        
        for complexity_level, count in complexity_distribution.items():
            if count == 0:
                continue
                
            if self.scenario_generation_mode == "llm":
                batch_scenarios = await self.generate_llm_scenarios(agent_type, count, complexity_level)
            elif self.scenario_generation_mode == "static":
                batch_scenarios = self.generate_static_scenarios(agent_type, count, complexity_level)
            else:  # hybrid
                # 70% LLM, 30% static
                llm_count = int(count * 0.7)
                static_count = count - llm_count
                
                batch_scenarios = []
                if llm_count > 0:
                    batch_scenarios.extend(await self.generate_llm_scenarios(agent_type, llm_count, complexity_level))
                if static_count > 0:
                    batch_scenarios.extend(self.generate_static_scenarios(agent_type, static_count, complexity_level))
            
            scenarios.extend(batch_scenarios)
        
        return scenarios

    async def generate_all_scenarios(self) -> List[SyntheticScenario]:
        """Gera todos os cenários para todos os agentes"""
        all_scenarios = []
        
        # Agentes individuais
        agent_types = ["alice", "bob", "main"]
        
        # Incluir swarm se habilitado
        if self.include_swarm_scenarios:
            agent_types.append("swarm")
        
        print(f"🔄 Gerando cenários para {len(agent_types)} tipos de agente...")
        
        for agent_type in agent_types:
            print(f"   📝 Gerando cenários para {agent_type}...")
            scenarios = await self.generate_scenarios_for_agent(agent_type)
            all_scenarios.extend(scenarios)
            print(f"   ✅ {len(scenarios)} cenários gerados para {agent_type}")
        
        print(f"🎯 Total de cenários gerados: {len(all_scenarios)}")
        return all_scenarios

    async def execute_scenario(self, scenario: SyntheticScenario) -> ExecutionResult:
        """Executa um cenário específico"""
        start_time = datetime.now()
        
        try:
            # Configurar thread config
            thread_config = {
                "configurable": {
                    "thread_id": f"synthetic-{uuid.uuid4().hex[:8]}-{scenario.agent_type}-{int(datetime.now().timestamp())}"
                }
            }
            
            # Inicializar estado
            initial_state = {
                "messages": [HumanMessage(content=scenario.user_input)],
                **scenario.state_context
            }
            
            # Executar baseado no tipo de agente
            if scenario.agent_type == "alice":
                agent = build_alice_agent(self.model)
                response = await agent.ainvoke(initial_state, thread_config)
                
            elif scenario.agent_type == "bob":
                agent = build_bob_agent(self.model)
                response = await agent.ainvoke(initial_state, thread_config)
                
            elif scenario.agent_type == "main":
                agent = build_main_agent(self.model)
                response = await agent.ainvoke(initial_state, thread_config)
                
            elif scenario.agent_type == "swarm":
                # Usar o sistema de swarm completo
                swarm_graph = create_multi_agent_system_swarm_mode()
                response = await swarm_graph.ainvoke(initial_state, thread_config)
            
            else:
                raise ValueError(f"Tipo de agente não suportado: {scenario.agent_type}")
            
            # Calcular tempo de execução
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Extrair handoffs se disponível
            handoffs_performed = []
            if "messages" in response:
                for msg in response["messages"]:
                    if hasattr(msg, 'additional_kwargs') and 'handoff' in str(msg.additional_kwargs):
                        handoffs_performed.append(str(msg.additional_kwargs))
            
            # Criar resultado
            result = ExecutionResult(
                scenario=scenario,
                trace_id=thread_config["configurable"]["thread_id"],
                execution_time=execution_time,
                success=True,
                response_messages=response.get("messages", []),
                structured_response=response.get("structured_response"),
                handoffs_performed=handoffs_performed
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ExecutionResult(
                scenario=scenario,
                trace_id=f"failed-{uuid.uuid4().hex[:8]}",
                execution_time=execution_time,
                success=False,
                error=str(e)
            )

    async def execute_all_scenarios(self, scenarios: List[SyntheticScenario]) -> List[ExecutionResult]:
        """Executa todos os cenários"""
        print(f"🚀 Executando {len(scenarios)} cenários...")
        
        results = []
        for i, scenario in enumerate(scenarios):
            print(f"   ⏳ Executando cenário {i+1}/{len(scenarios)} ({scenario.agent_type})")
            result = await self.execute_scenario(scenario)
            results.append(result)
            
            if result.success:
                print(f"   ✅ Cenário {i+1} executado com sucesso")
            else:
                print(f"   ❌ Cenário {i+1} falhou: {result.error}")
        
        return results

    def generate_report(self, results: List[ExecutionResult]) -> Dict[str, Any]:
        """Gera relatório dos resultados"""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        # Estatísticas por agente
        stats_by_agent = {}
        for result in results:
            agent_type = result.scenario.agent_type
            if agent_type not in stats_by_agent:
                stats_by_agent[agent_type] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_execution_time": 0,
                    "handoffs_detected": 0
                }
            
            stats_by_agent[agent_type]["total"] += 1
            if result.success:
                stats_by_agent[agent_type]["successful"] += 1
            else:
                stats_by_agent[agent_type]["failed"] += 1
            
            stats_by_agent[agent_type]["avg_execution_time"] += result.execution_time
            
            if result.handoffs_performed:
                stats_by_agent[agent_type]["handoffs_detected"] += len(result.handoffs_performed)
        
        # Calcular médias
        for agent_type, stats in stats_by_agent.items():
            if stats["total"] > 0:
                stats["avg_execution_time"] /= stats["total"]
                stats["success_rate"] = (stats["successful"] / stats["total"]) * 100
        
        # Estatísticas por complexidade
        stats_by_complexity = {}
        for result in results:
            complexity = result.scenario.complexity_level
            if complexity not in stats_by_complexity:
                stats_by_complexity[complexity] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_execution_time": 0
                }
            
            stats_by_complexity[complexity]["total"] += 1
            if result.success:
                stats_by_complexity[complexity]["successful"] += 1
            else:
                stats_by_complexity[complexity]["failed"] += 1
            
            stats_by_complexity[complexity]["avg_execution_time"] += result.execution_time
        
        # Calcular médias de complexidade
        for complexity, stats in stats_by_complexity.items():
            if stats["total"] > 0:
                stats["avg_execution_time"] /= stats["total"]
                stats["success_rate"] = (stats["successful"] / stats["total"]) * 100
        
        # Estatísticas por método de geração
        stats_by_generation = {}
        for result in results:
            method = result.scenario.metadata.get("generation_method", "unknown")
            if method not in stats_by_generation:
                stats_by_generation[method] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0
                }
            
            stats_by_generation[method]["total"] += 1
            if result.success:
                stats_by_generation[method]["successful"] += 1
            else:
                stats_by_generation[method]["failed"] += 1
        
        # Calcular taxas de sucesso por método
        for method, stats in stats_by_generation.items():
            if stats["total"] > 0:
                stats["success_rate"] = (stats["successful"] / stats["total"]) * 100
        
        total_execution_time = sum(r.execution_time for r in results)
        
        return {
            "summary": {
                "total_scenarios": len(results),
                "successful_scenarios": len(successful),
                "failed_scenarios": len(failed),
                "overall_success_rate": (len(successful) / len(results) * 100) if results else 0,
                "total_execution_time": total_execution_time,
                "avg_execution_time": total_execution_time / len(results) if results else 0
            },
            "stats_by_agent": stats_by_agent,
            "stats_by_complexity": stats_by_complexity,
            "stats_by_generation_method": stats_by_generation,
            "langsmith_project": self.langsmith_project_name,
            "configuration": {
                "model_name": self.model_name,
                "temperature": self.temperature,
                "num_scenarios_per_agent": self.num_scenarios_per_agent,
                "include_swarm_scenarios": self.include_swarm_scenarios,
                "scenario_generation_mode": self.scenario_generation_mode
            },
            "failed_scenarios": [
                {
                    "agent_type": r.scenario.agent_type,
                    "user_input": r.scenario.user_input,
                    "error": r.error,
                    "complexity": r.scenario.complexity_level
                }
                for r in failed
            ],
            "generation_timestamp": datetime.now().isoformat()
        }

    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Salva relatório em arquivo JSON"""
        if filename is None:
            filename = f"synthetic_data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Relatório salvo em: {filename}")


async def main():
    """Função principal para execução do gerador"""
    generator = SyntheticDataGenerator(
        model_name="openai:gpt-4o-mini",
        temperature=0.7,
        num_scenarios_per_agent=5,  # Menor para teste
        include_swarm_scenarios=True,
        scenario_generation_mode="hybrid"
    )
    
    # Gerar cenários
    scenarios = await generator.generate_all_scenarios()
    
    # Executar cenários
    results = await generator.execute_all_scenarios(scenarios)
    
    # Gerar relatório
    report = generator.generate_report(results)
    
    # Salvar relatório
    generator.save_report(report)
    
    # Imprimir resumo
    print("\n" + "="*60)
    print("📊 RESUMO DA EXECUÇÃO")
    print("="*60)
    print(f"🎯 Total de cenários: {report['summary']['total_scenarios']}")
    print(f"✅ Sucessos: {report['summary']['successful_scenarios']}")
    print(f"❌ Falhas: {report['summary']['failed_scenarios']}")
    print(f"📈 Taxa de sucesso: {report['summary']['overall_success_rate']:.1f}%")
    print(f"⏱️  Tempo total: {report['summary']['total_execution_time']:.2f}s")
    print(f"🔗 Projeto LangSmith: {report['langsmith_project']}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main()) 