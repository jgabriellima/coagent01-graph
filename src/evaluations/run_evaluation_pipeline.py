#!/usr/bin/env python3
"""
Pipeline Completo de Evaluation
------------------------------

Este script executa o pipeline completo de evaluation:
1. Gera dados sintéticos baseados no sistema de swarm agents
2. Executa cenários nos agentes para coletar traces via LangSmith
3. Executa suite de evaluators nos traces coletados
4. Gera relatórios consolidados

Uso:
    python run_evaluation_pipeline.py [OPTIONS]

Exemplos:
    # Pipeline completo
    python run_evaluation_pipeline.py --project "my-evaluation" --scenarios 20
    
    # Pipeline rápido para testes
    python run_evaluation_pipeline.py --quick-test
    
    # Apenas geração de dados sintéticos
    python run_evaluation_pipeline.py --only-generate
    
    # Apenas evaluation (usar dados existentes)
    python run_evaluation_pipeline.py --only-evaluate --project "existing-project"
"""

import argparse
import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Adicionar o diretório raiz do projeto ao sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.evaluations.synthetic_data_generator import SyntheticDataGenerator
from src.evaluations.evaluators.run_evaluations import EvaluationRunner
from src.evaluations.evaluators.evaluator_registry import get_evaluators_for_profile
from langsmith import Client


def parse_args():
    """Processa argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description="Pipeline Completo de Evaluation para Sistema de Swarm Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s --project "my-evaluation" --scenarios 20
  %(prog)s --quick-test
  %(prog)s --only-generate --scenarios 10
  %(prog)s --only-evaluate --project "existing-project"
        """
    )
    
    # Configurações gerais
    parser.add_argument(
        "--project",
        type=str,
        help="Nome do projeto LangSmith (padrão: evaluation-pipeline-TIMESTAMP)"
    )
    
    parser.add_argument(
        "--scenarios",
        type=int,
        default=15,
        help="Número de cenários por agente (padrão: 15)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="openai:gpt-4o-mini",
        help="Modelo a usar (padrão: openai:gpt-4o-mini)"
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperatura do modelo (padrão: 0.7)"
    )
    
    parser.add_argument(
        "--include-swarm",
        action="store_true",
        default=True,
        help="Incluir cenários de swarm workflow (padrão: True)"
    )
    
    parser.add_argument(
        "--no-swarm",
        action="store_true",
        help="Excluir cenários de swarm workflow"
    )
    
    parser.add_argument(
        "--generation-mode",
        type=str,
        choices=["static", "llm", "hybrid"],
        default="hybrid",
        help="Modo de geração de cenários (padrão: hybrid)"
    )
    
    # Modo de execução
    parser.add_argument(
        "--only-generate",
        action="store_true",
        help="Apenas gerar dados sintéticos, não executar evaluation"
    )
    
    parser.add_argument(
        "--only-evaluate",
        action="store_true",
        help="Apenas executar evaluation em dados existentes"
    )
    
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Execução rápida com poucos cenários para teste"
    )
    
    # Configurações de evaluation
    parser.add_argument(
        "--evaluator-profile",
        type=str,
        default="agentic",
        choices=["agentic", "comprehensive", "minimal"],
        help="Perfil de evaluators a usar (padrão: agentic)"
    )
    
    parser.add_argument(
        "--evaluation-model",
        type=str,
        default="openai:gpt-4o",
        help="Modelo para evaluation (padrão: openai:gpt-4o)"
    )
    
    # Configurações de saída
    parser.add_argument(
        "--output-dir",
        type=str,
        default="sample_agent/evaluations/results",
        help="Diretório para salvar resultados (padrão: sample_agent/evaluations/results)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Saída detalhada durante a execução"
    )
    
    return parser.parse_args()


class EvaluationPipeline:
    """Pipeline completo de evaluation"""
    
    def __init__(self, args):
        self.args = args
        self.project_name = args.project or f"evaluation-pipeline-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.output_dir = Path(args.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar LangSmith client
        self.langsmith_client = None
        if os.getenv("LANGSMITH_API_KEY"):
            try:
                self.langsmith_client = Client()
            except Exception as e:
                print(f"⚠️  Erro ao configurar LangSmith: {e}")
    
    async def run_data_generation(self) -> Dict[str, Any]:
        """Executa geração de dados sintéticos"""
        print("🎲 FASE 1: Geração de Dados Sintéticos")
        print("="*50)
        
        # Resolver configuração do swarm
        include_swarm = self.args.include_swarm and not self.args.no_swarm
        
        # Configurar gerador
        generator = SyntheticDataGenerator(
            model_name=self.args.model,
            temperature=self.args.temperature,
            langsmith_project_name=self.project_name,
            num_scenarios_per_agent=self.args.scenarios,
            include_swarm_scenarios=include_swarm,
            scenario_generation_mode=self.args.generation_mode
        )
        
        # Gerar e executar cenários
        scenarios = await generator.generate_all_scenarios()
        results = await generator.execute_all_scenarios(scenarios)
        
        # Gerar relatório
        report = generator.generate_report(results)
        
        # Salvar relatório
        report_path = self.output_dir / f"synthetic_data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dados sintéticos gerados e executados")
        print(f"📄 Relatório salvo em: {report_path}")
        print(f"📊 Projeto LangSmith: {self.project_name}")
        
        return report
    
    async def run_evaluation(self) -> Dict[str, Any]:
        """Executa suite de evaluators"""
        print(f"\n🔍 FASE 2: Execution de Evaluators")
        print("="*50)
        
        if not self.langsmith_client:
            print("❌ LangSmith client não disponível. Não é possível executar evaluators.")
            return {}
        
        try:
            # Obter runs do projeto
            runs = list(self.langsmith_client.list_runs(project_name=self.project_name))
            
            if not runs:
                print(f"⚠️  Nenhum run encontrado no projeto: {self.project_name}")
                return {}
            
            print(f"📊 Encontrados {len(runs)} runs para evaluation")
            
            # Obter evaluators para o perfil especificado
            evaluators_list = get_evaluators_for_profile(self.args.evaluator_profile)
            evaluators = {evaluator.name(): evaluator for evaluator in evaluators_list}
            
            print(f"🔧 Usando perfil '{self.args.evaluator_profile}' com {len(evaluators)} evaluators:")
            for name in evaluators.keys():
                print(f"   - {name}")
            print()
            
            # Configurar runner
            runner = EvaluationRunner(
                evaluators=evaluators,
                langsmith_client=self.langsmith_client,
                evaluation_model=self.args.evaluation_model
            )
            
            # Executar evaluations
            results = await runner.run_evaluations(
                project_name=self.project_name,
                max_runs=None,  # Avaliar todos os runs
                batch_size=10
            )
            
            # Salvar resultados
            results_path = self.output_dir / f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Evaluation concluída")
            print(f"📄 Resultados salvos em: {results_path}")
            
            return results
            
        except Exception as e:
            print(f"❌ Erro durante evaluation: {e}")
            if self.args.verbose:
                import traceback
                traceback.print_exc()
            return {}
    
    def generate_consolidated_report(self, data_report: Dict[str, Any], eval_results: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório consolidado"""
        print(f"\n📊 FASE 3: Geração de Relatório Consolidado")
        print("="*50)
        
        # Consolidar métricas
        consolidated = {
            "pipeline_summary": {
                "project_name": self.project_name,
                "executed_at": datetime.now().isoformat(),
                "configuration": {
                    "model": self.args.model,
                    "temperature": self.args.temperature,
                    "scenarios_per_agent": self.args.scenarios,
                    "evaluator_profile": self.args.evaluator_profile,
                    "evaluation_model": self.args.evaluation_model
                }
            },
            "data_generation": data_report.get("summary", {}),
            "evaluation_results": eval_results.get("summary", {}),
            "detailed_results": {
                "data_generation": data_report,
                "evaluation": eval_results
            }
        }
        
        # Calcular métricas combinadas
        if data_report and eval_results:
            # Taxa de sucesso geral
            data_success_rate = data_report.get("summary", {}).get("success_rate", 0)
            eval_success_rate = eval_results.get("summary", {}).get("success_rate", 0)
            
            consolidated["pipeline_summary"]["overall_success_rate"] = (data_success_rate + eval_success_rate) / 2
            
            # Tempo total
            data_time = data_report.get("summary", {}).get("avg_execution_time", 0)
            eval_time = eval_results.get("summary", {}).get("avg_evaluation_time", 0)
            
            consolidated["pipeline_summary"]["total_avg_time"] = data_time + eval_time
        
        # Salvar relatório consolidado
        report_path = self.output_dir / f"consolidated_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Relatório consolidado gerado")
        print(f"📄 Relatório salvo em: {report_path}")
        
        return consolidated
    
    def print_summary(self, consolidated_report: Dict[str, Any]):
        """Imprime resumo final"""
        print("\n" + "="*70)
        print("📊 RESUMO FINAL DO PIPELINE")
        print("="*70)
        
        summary = consolidated_report.get("pipeline_summary", {})
        data_summary = consolidated_report.get("data_generation", {})
        eval_summary = consolidated_report.get("evaluation_results", {})
        
        print(f"🎯 Projeto: {summary.get('project_name', 'N/A')}")
        print(f"⚙️  Modelo: {summary.get('configuration', {}).get('model', 'N/A')}")
        print(f"📈 Perfil de Evaluation: {summary.get('configuration', {}).get('evaluator_profile', 'N/A')}")
        
        if data_summary:
            print(f"\n📊 Geração de Dados:")
            print(f"   Cenários: {data_summary.get('total_scenarios', 0)}")
            print(f"   Sucessos: {data_summary.get('successful', 0)}")
            print(f"   Taxa de sucesso: {data_summary.get('success_rate', 0):.1f}%")
            print(f"   Tempo médio: {data_summary.get('avg_execution_time', 0):.2f}s")
        
        if eval_summary:
            print(f"\n🔍 Evaluation:")
            print(f"   Runs avaliados: {eval_summary.get('total_runs', 0)}")
            print(f"   Evaluators executados: {eval_summary.get('evaluators_executed', 0)}")
            print(f"   Taxa de sucesso: {eval_summary.get('success_rate', 0):.1f}%")
        
        overall_success = summary.get("overall_success_rate", 0)
        if overall_success > 0:
            print(f"\n🎯 Taxa de Sucesso Geral: {overall_success:.1f}%")
        
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"1. Analise os resultados detalhados nos arquivos JSON")
        print(f"2. Verifique traces e métricas no LangSmith dashboard")
        print(f"3. Ajuste configurações baseado nos resultados")
        print(f"4. Execute novamente com configurações otimizadas")
        
        if overall_success < 80:
            print(f"\n⚠️  Taxa de sucesso baixa ({overall_success:.1f}%)")
            print(f"   Considere revisar configurações dos agentes ou evaluators")
    
    async def run_pipeline(self):
        """Executa pipeline completo"""
        print("🚀 INICIANDO PIPELINE DE EVALUATION")
        print("="*70)
        print(f"Projeto: {self.project_name}")
        print(f"Cenários por agente: {self.args.scenarios}")
        print(f"Perfil de evaluators: {self.args.evaluator_profile}")
        print(f"Diretório de saída: {self.output_dir}")
        print(f"Incluir swarm: {self.args.include_swarm and not self.args.no_swarm}")
        print(f"Modo de geração: {self.args.generation_mode}")
        print()
        
        data_report = {}
        eval_results = {}
        
        try:
            # Fase 1: Geração de dados sintéticos
            if not self.args.only_evaluate:
                data_report = await self.run_data_generation()
            
            # Fase 2: Execution de evaluators
            if not self.args.only_generate:
                eval_results = await self.run_evaluation()
            
            # Fase 3: Relatório consolidado
            consolidated_report = self.generate_consolidated_report(data_report, eval_results)
            
            # Resumo final
            self.print_summary(consolidated_report)
            
        except Exception as e:
            print(f"❌ Erro no pipeline: {e}")
            if self.args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)


async def main():
    """Função principal"""
    args = parse_args()
    
    # Configurações para teste rápido
    if args.quick_test:
        args.scenarios = 3
        args.evaluator_profile = "minimal"
        args.project = args.project or "quick-test-pipeline"
        print("🚀 Modo de teste rápido ativado!")
    
    # Verificar variáveis de ambiente
    if not os.getenv("LANGSMITH_API_KEY"):
        print("⚠️  LANGSMITH_API_KEY não encontrada!")
        if not args.only_generate:
            print("   Evaluation não será executada sem API key do LangSmith")
            print("   Use --only-generate para apenas gerar dados sintéticos")
        print()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY não encontrada!")
        print("   Configure sua API key OpenAI para continuar")
        sys.exit(1)
    
    # Executar pipeline
    pipeline = EvaluationPipeline(args)
    await pipeline.run_pipeline()


if __name__ == "__main__":
    asyncio.run(main()) 