#!/usr/bin/env python3
"""
Script para executar o Gerador de Dados Sintéticos
-------------------------------------------------

Uso:
    python run_synthetic_data_generator.py [OPTIONS]

Exemplos:
    # Execução básica
    python run_synthetic_data_generator.py
    
    # Configuração personalizada
    python run_synthetic_data_generator.py --project "my-evaluation-project-20250712" --scenarios 20 --model gpt-4o-mini
    
    # Execução rápida para testes
    python run_synthetic_data_generator.py --scenarios 5 --project "quick-test"
    
    # Incluir cenários de swarm
    python run_synthetic_data_generator.py --include-swarm --generation-mode llm
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz do projeto ao sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.evaluations.synthetic_data_generator import SyntheticDataGenerator


def parse_args():
    """Processa argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description="Gerador de Dados Sintéticos para Sistema de Swarm Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s
  %(prog)s --project "my-evaluation-project" --scenarios 20
  %(prog)s --model "openai:gpt-4o" --temperature 0.5
  %(prog)s --scenarios 5 --project "quick-test"
  %(prog)s --include-swarm --generation-mode llm
        """
    )
    
    parser.add_argument(
        "--project",
        type=str,
        help="Nome do projeto LangSmith (padrão: synthetic-swarm-evaluation-TIMESTAMP)"
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
        "--output-dir",
        type=str,
        default="sample_agent/evaluations",
        help="Diretório para salvar relatórios (padrão: sample_agent/evaluations)"
    )
    
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Execução rápida com poucos cenários para teste"
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
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Saída detalhada durante a execução"
    )
    
    return parser.parse_args()


async def main():
    """Função principal"""
    args = parse_args()
    
    # Configurações para teste rápido
    if args.quick_test:
        args.scenarios = 3
        args.project = args.project or "quick-test"
        print("🚀 Modo de teste rápido ativado!")
    
    # Resolver configuração do swarm
    include_swarm = args.include_swarm and not args.no_swarm
    
    # Verificar variáveis de ambiente necessárias
    if not os.getenv("LANGSMITH_API_KEY"):
        print("⚠️  LANGSMITH_API_KEY não encontrada!")
        print("   Configure sua API key para coletar traces:")
        print("   export LANGSMITH_API_KEY=your_api_key_here")
        print("   Continuando sem coleta de traces...")
        print()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY não encontrada!")
        print("   Configure sua API key OpenAI:")
        print("   export OPENAI_API_KEY=your_api_key_here")
        print("   Interrompendo execução...")
        sys.exit(1)
    
    # Configurar gerador
    print("🔧 Configurando gerador de dados sintéticos...")
    print(f"   Modelo: {args.model}")
    print(f"   Temperatura: {args.temperature}")
    print(f"   Cenários por agente: {args.scenarios}")
    print(f"   Projeto LangSmith: {args.project or 'auto-generated'}")
    print(f"   Incluir swarm: {include_swarm}")
    print(f"   Modo de geração: {args.generation_mode}")
    print()
    
    try:
        generator = SyntheticDataGenerator(
            model_name=args.model,
            temperature=args.temperature,
            langsmith_project_name=args.project,
            num_scenarios_per_agent=args.scenarios,
            include_swarm_scenarios=include_swarm,
            scenario_generation_mode=args.generation_mode
        )
        
        # Gerar cenários
        print("🎲 Gerando cenários sintéticos...")
        scenarios = await generator.generate_all_scenarios()
        
        if args.verbose:
            print("\n📋 Cenários gerados:")
            for i, scenario in enumerate(scenarios[:5]):  # Mostrar apenas os primeiros 5
                print(f"   {i+1}. {scenario.agent_type}: {scenario.user_input}")
            if len(scenarios) > 5:
                print(f"   ... e mais {len(scenarios) - 5} cenários")
            print()
        
        # Executar cenários
        print("🚀 Executando cenários nos agentes...")
        results = await generator.execute_all_scenarios(scenarios)
        
        # Gerar relatório
        print("📊 Gerando relatório...")
        report = generator.generate_report(results)
        
        # Salvar relatório
        generator.save_report(report)
        
        # Exibir resumo
        print("\n" + "="*60)
        print("📊 RESUMO DA EXECUÇÃO")
        print("="*60)
        print(f"🎯 Total de cenários: {report['summary']['total_scenarios']}")
        print(f"✅ Sucessos: {report['summary']['successful_scenarios']}")
        print(f"❌ Falhas: {report['summary']['failed_scenarios']}")
        print(f"📈 Taxa de sucesso: {report['summary']['overall_success_rate']:.1f}%")
        print(f"⏱️  Tempo total: {report['summary']['total_execution_time']:.2f}s")
        print(f"🔗 Projeto LangSmith: {report['langsmith_project']}")
        
        print(f"\n📈 Estatísticas por agente:")
        for agent, stats in report['stats_by_agent'].items():
            print(f"  {agent.capitalize()}: {stats['successful']}/{stats['total']} sucessos ({stats['success_rate']:.1f}%)")
            if stats['handoffs_detected'] > 0:
                print(f"    🔄 Handoffs detectados: {stats['handoffs_detected']}")
        
        print(f"\n🎯 Estatísticas por complexidade:")
        for complexity, stats in report['stats_by_complexity'].items():
            print(f"  {complexity.capitalize()}: {stats['successful']}/{stats['total']} sucessos ({stats['success_rate']:.1f}%)")
        
        if report['stats_by_generation_method']:
            print(f"\n🤖 Estatísticas por método de geração:")
            for method, stats in report['stats_by_generation_method'].items():
                print(f"  {method.capitalize()}: {stats['successful']}/{stats['total']} sucessos ({stats['success_rate']:.1f}%)")
        
        if report['failed_scenarios']:
            print(f"\n❌ {len(report['failed_scenarios'])} cenários falharam:")
            for failure in report['failed_scenarios'][:3]:  # Mostrar apenas os primeiros 3
                print(f"  - {failure['agent_type']}: {failure['error'][:80]}...")
        
        # Próximos passos
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Verifique os traces no LangSmith dashboard")
        print("2. Execute a suite de evaluators nos dados coletados")
        print("3. Analise métricas de performance dos agentes")
        print("4. Ajuste configurações baseado nos resultados")
        
        if report['summary']['overall_success_rate'] < 80:
            print(f"\n⚠️  Taxa de sucesso baixa ({report['summary']['overall_success_rate']:.1f}%)")
            print("   Considere revisar a configuração dos agentes")
        
        if args.quick_test:
            print("\n🧪 Teste rápido concluído!")
            print("   Execute sem --quick-test para geração completa")
        
        print("="*60)
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 