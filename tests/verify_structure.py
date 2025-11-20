"""
Script de verificação da organização do projeto
Verifica se todos os arquivos e diretórios estão nos lugares corretos
"""
import os
from pathlib import Path

def check_structure():
    """Verifica estrutura de diretórios"""
    base_dir = Path(__file__).parent.parent
    
    print("🔍 VERIFICANDO ESTRUTURA DO PROJETO")
    print("=" * 60)
    
    # Diretórios esperados
    expected_dirs = {
        'src': 'Código fonte SOLID',
        'scripts': 'Scripts PowerShell',
        'data': 'Dados coletados',
        'docs': 'Documentação',
        'tests': 'Testes (futuro)'
    }
    
    print("\n📁 Diretórios:")
    all_dirs_ok = True
    for dir_name, description in expected_dirs.items():
        dir_path = base_dir / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        status = "✅" if exists else "❌"
        print(f"  {status} {dir_name:15s} - {description}")
        if not exists:
            all_dirs_ok = False
    
    # Arquivos esperados no src/
    src_files = ['__init__.py', 'config.py', 'models.py', 'repositories.py', 'services.py']
    print("\n📄 Arquivos em src/:")
    src_ok = True
    for file_name in src_files:
        file_path = base_dir / 'src' / file_name
        exists = file_path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {file_name}")
        if not exists:
            src_ok = False
    
    # Arquivos de configuração
    config_files = {
        '.env': 'Configurações (pode não existir)',
        '.env.example': 'Template de configuração',
        'requirements.txt': 'Dependências Python',
        'README.md': 'Documentação principal',
        '.gitignore': 'Arquivos ignorados'
    }
    
    print("\n⚙️  Arquivos de Configuração:")
    config_ok = True
    for file_name, description in config_files.items():
        file_path = base_dir / file_name
        exists = file_path.exists()
        status = "✅" if exists else "⚠️"
        print(f"  {status} {file_name:20s} - {description}")
        if not exists and file_name != '.env':
            config_ok = False
    
    # Arquivos principais Python
    main_scripts = {
        'collect_news_bbas3.py': 'Script principal de coleta'
    }
    
    print("\n🐍 Scripts Principais:")
    scripts_ok = True
    for file_name, description in main_scripts.items():
        file_path = base_dir / file_name
        exists = file_path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {file_name:25s} - {description}")
        if not exists:
            scripts_ok = False
    
    # Verificar scripts movidos para scripts/
    analysis_scripts = {
        'scripts/sentimentos.py': 'Análise de sentimentos',
        'scripts/analise_detalhada.py': 'Análise detalhada',
        'scripts/analisar_dados_mong.py': 'Análise Snowflake',
        'scripts/buscar_dados_reais.py': 'Coleta Yahoo Finance'
    }
    
    print("\n📊 Scripts de Análise (scripts/):")
    for file_name, description in analysis_scripts.items():
        file_path = base_dir / file_name
        exists = file_path.exists()
        status = "✅" if exists else "❌"
        script_name = file_name.split('/')[-1]
        print(f"  {status} {script_name:30s} - {description}")
    
    # Verificar scripts de teste movidos para tests/
    test_scripts = {
        'tests/test_system.py': 'Suite de testes',
        'tests/verify_mongo_data.py': 'Validação MongoDB',
        'tests/testConnection.py': 'Teste de conexões'
    }
    
    print("\n🧪 Scripts de Teste (tests/):")
    for file_name, description in test_scripts.items():
        file_path = base_dir / file_name
        exists = file_path.exists()
        status = "✅" if exists else "❌"
        script_name = file_name.split('/')[-1]
        print(f"  {status} {script_name:30s} - {description}")
    
    # Documentação
    doc_files = ['INDEX.md', 'ESTRUTURA.md', 'ARQUITETURA.md', 'CHANGELOG.md']
    print("\n📚 Documentação (docs/):")
    docs_ok = True
    for file_name in doc_files:
        file_path = base_dir / 'docs' / file_name
        exists = file_path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {file_name}")
        if not exists:
            docs_ok = False
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("=" * 60)
    
    checks = {
        'Diretórios': all_dirs_ok,
        'Código fonte (src/)': src_ok,
        'Configuração': config_ok,
        'Scripts principais': scripts_ok,
        'Documentação': docs_ok
    }
    
    all_ok = all(checks.values())
    
    for check_name, status in checks.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check_name}")
    
    print("=" * 60)
    if all_ok:
        print("🎉 ESTRUTURA DO PROJETO: OK!")
        print("\n💡 Próximo passo: pip install python-dotenv")
        print("💡 Depois execute: python collect_news_bbas3.py")
    else:
        print("⚠️  Algumas verificações falharam. Verifique acima.")
    
    return all_ok

if __name__ == '__main__':
    check_structure()
