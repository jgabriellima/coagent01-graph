#!/usr/bin/env python3
"""
Script de Setup para Sistema de Dados Sintéticos
-----------------------------------------------

Este script configura o ambiente para o sistema de geração de dados sintéticos:
- Verifica dependências
- Configura permissões de arquivos
- Cria diretórios necessários
- Valida configuração

Uso:
    python setup_synthetic_data.py
"""

import os
import sys
import stat
import subprocess
from pathlib import Path


def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        print(f"   Versão atual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    required_packages = [
        'langchain',
        'langsmith',
        'openai',
        'deepeval',
        'pandas',
        'numpy',
        'asyncio',
        'aiohttp',
        'pydantic',
        'jinja2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Pacotes faltando: {', '.join(missing_packages)}")
        print("   Execute: pip install -r requirements.txt")
        return False
    
    return True


def check_environment_variables():
    """Verifica variáveis de ambiente necessárias"""
    required_vars = ['OPENAI_API_KEY']
    optional_vars = ['LANGSMITH_API_KEY', 'LANGCHAIN_TRACING_V2']
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}")
        else:
            missing_required.append(var)
            print(f"❌ {var}")
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var}")
        else:
            missing_optional.append(var)
            print(f"⚠️  {var}")
    
    if missing_required:
        print(f"\n❌ Variáveis obrigatórias faltando: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Variáveis opcionais faltando: {', '.join(missing_optional)}")
        print("   LangSmith não funcionará sem LANGSMITH_API_KEY")
    
    return True


def make_executable(file_path):
    """Torna um arquivo executável"""
    try:
        current_permissions = os.stat(file_path).st_mode
        os.chmod(file_path, current_permissions | stat.S_IEXEC)
        print(f"✅ {file_path} - executável")
        return True
    except Exception as e:
        print(f"❌ {file_path} - erro: {e}")
        return False


def setup_file_permissions():
    """Configura permissões dos arquivos"""
    print("\n🔧 Configurando permissões de arquivos...")
    
    scripts_dir = Path(__file__).parent
    executable_files = [
        scripts_dir / "synthetic_data_generator.py",
        scripts_dir / "run_synthetic_data_generator.py",
        scripts_dir / "run_evaluation_pipeline.py",
        scripts_dir / "setup_synthetic_data.py"
    ]
    
    success = True
    for file_path in executable_files:
        if file_path.exists():
            if not make_executable(file_path):
                success = False
        else:
            print(f"⚠️  Arquivo não encontrado: {file_path}")
    
    return success


def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando diretórios necessários...")
    
    base_dir = Path(__file__).parent
    directories = [
        base_dir / "results",
        base_dir / "data",
        base_dir / "logs"
    ]
    
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ {directory}")
        except Exception as e:
            print(f"❌ {directory} - erro: {e}")
            return False
    
    return True


def test_imports():
    """Testa importações dos módulos principais"""
    print("\n🧪 Testando importações dos módulos...")
    
    try:
        from sample_agent.evaluations.synthetic_data_generator import SyntheticDataGenerator
        print("✅ SyntheticDataGenerator")
    except ImportError as e:
        print(f"❌ SyntheticDataGenerator - erro: {e}")
        return False
    
    try:
        from sample_agent.evaluations.evaluators.evaluator_registry import EvaluatorRegistry
        print("✅ EvaluatorRegistry")
    except ImportError as e:
        print(f"❌ EvaluatorRegistry - erro: {e}")
        return False
    
    try:
        from sample_agent.agents.swarm.alice_agent import build_alice_agent
        from sample_agent.agents.swarm.bob_agent import build_bob_agent
        from sample_agent.agents.swarm.main_agent import build_main_agent
        print("✅ Swarm Agents")
    except ImportError as e:
        print(f"❌ Swarm Agents - erro: {e}")
        return False
    
    return True


def create_example_config():
    """Cria arquivo de configuração de exemplo"""
    print("\n📝 Criando arquivo de configuração de exemplo...")
    
    config_content = """# Configuração para Sistema de Dados Sintéticos
# Copie este arquivo para .env e configure suas variáveis

# Obrigatório
OPENAI_API_KEY=sua_openai_api_key_aqui

# Opcional (para LangSmith)
LANGSMITH_API_KEY=sua_langsmith_api_key_aqui
LANGCHAIN_TRACING_V2=true

# Configurações do sistema
LANGSMITH_PROJECT=synthetic-data-evaluation
"""
    
    config_path = Path(__file__).parent / "example.env"
    
    try:
        with open(config_path, "w") as f:
            f.write(config_content)
        print(f"✅ Arquivo criado: {config_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar configuração: {e}")
        return False


def print_usage_examples():
    """Imprime exemplos de uso"""
    print("\n🎯 EXEMPLOS DE USO:")
    print("="*50)
    
    print("\n1. Teste rápido:")
    print("   python run_evaluation_pipeline.py --quick-test")
    
    print("\n2. Geração completa de dados:")
    print("   python run_synthetic_data_generator.py --scenarios 20")
    
    print("\n3. Pipeline completo:")
    print("   python run_evaluation_pipeline.py \\")
    print("     --project 'minha-avaliacao' \\")
    print("     --scenarios 25 \\")
    print("     --evaluator-profile 'comprehensive'")
    
    print("\n4. Apenas evaluation:")
    print("   python run_evaluation_pipeline.py \\")
    print("     --only-evaluate \\")
    print("     --project 'projeto-existente'")


def main():
    """Função principal de setup"""
    print("🚀 SETUP - Sistema de Dados Sintéticos")
    print("="*50)
    
    success = True
    
    # Verificar Python
    print("\n🐍 Verificando Python...")
    if not check_python_version():
        success = False
    
    # Verificar dependências
    print("\n📦 Verificando dependências...")
    if not check_dependencies():
        success = False
    
    # Verificar variáveis de ambiente
    print("\n🔑 Verificando variáveis de ambiente...")
    if not check_environment_variables():
        success = False
    
    # Configurar permissões
    if not setup_file_permissions():
        success = False
    
    # Criar diretórios
    if not create_directories():
        success = False
    
    # Testar importações
    if not test_imports():
        success = False
    
    # Criar configuração de exemplo
    create_example_config()
    
    # Resumo
    print("\n" + "="*50)
    if success:
        print("✅ SETUP CONCLUÍDO COM SUCESSO!")
        print("\n🎯 Sistema pronto para uso!")
        print("   Configure suas API keys e execute os scripts.")
        print_usage_examples()
    else:
        print("❌ SETUP FALHOU!")
        print("\n🔧 Corrija os problemas acima e execute novamente.")
        print("   Consulte o README_synthetic_data.md para detalhes.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 