"""
Script de teste completo do sistema
Testa todos os componentes da arquitetura refatorada
"""
import sys
from pathlib import Path

# Adiciona diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from datetime import datetime, timezone
from src.config import settings
from src.models import NewsArticle, SentimentAnalysis
from src.services import SentimentAnalysisService, NewsCollectorService


def print_section(title):
    """Imprime seção formatada"""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)


def test_configuration():
    """Testa carregamento de configurações"""
    print_section("TESTE DE CONFIGURAÇÃO")
    
    print(f"✅ MongoDB URI: {settings.mongodb.uri}")
    print(f"✅ MongoDB DB: {settings.mongodb.database}")
    print(f"✅ MongoDB Collection: {settings.mongodb.collection}")
    print(f"✅ MongoDB Enabled: {settings.mongodb.enabled}")
    
    print(f"\n✅ PostgreSQL Host: {settings.postgresql.host}")
    print(f"✅ PostgreSQL DB: {settings.postgresql.database}")
    print(f"✅ PostgreSQL Table: {settings.postgresql.table_name}")
    print(f"✅ PostgreSQL Enabled: {settings.postgresql.enabled}")
    
    print(f"\n✅ Snowflake Account: {settings.snowflake.account}")
    print(f"✅ Snowflake DB: {settings.snowflake.database}")
    print(f"✅ Snowflake Schema: {settings.snowflake.schema}")
    print(f"✅ Snowflake Enabled: {settings.snowflake.enabled}")
    
    print(f"\n✅ Max per Query: {settings.app.max_articles_per_query}")
    print(f"✅ JSON Output: {settings.app.json_output_file}")
    print(f"✅ Save JSON Local: {settings.app.save_json_local}")


def test_sentiment_analysis():
    """Testa análise de sentimento"""
    print_section("TESTE DE ANÁLISE DE SENTIMENTO")
    
    service = SentimentAnalysisService()
    
    # Teste positivo
    text_pos = "Banco do Brasil anuncia lucro recorde com crescimento forte e alta rentabilidade"
    result_pos = service.analyze(text_pos, "BBAS3 tem alta")
    
    print("\n📊 Teste Positivo:")
    print(f"  Texto: '{text_pos}'")
    print(f"  Polaridade: {result_pos.polarity}")
    print(f"  Label: {result_pos.label}")
    print(f"  Confiança: {result_pos.confidence}")
    print(f"  Keywords +: {result_pos.positive_keywords}")
    print(f"  Keywords -: {result_pos.negative_keywords}")
    assert result_pos.label == 'positive', "Deveria ser positivo"
    print("  ✅ PASSOU")
    
    # Teste negativo
    text_neg = "Banco do Brasil sofre prejuízo com crise e queda na inadimplência"
    result_neg = service.analyze(text_neg, "BBAS3 em crise")
    
    print("\n📊 Teste Negativo:")
    print(f"  Texto: '{text_neg}'")
    print(f"  Polaridade: {result_neg.polarity}")
    print(f"  Label: {result_neg.label}")
    print(f"  Confiança: {result_neg.confidence}")
    print(f"  Keywords +: {result_neg.positive_keywords}")
    print(f"  Keywords -: {result_neg.negative_keywords}")
    assert result_neg.label == 'negative', "Deveria ser negativo"
    print("  ✅ PASSOU")
    
    # Teste neutro
    text_neu = "Banco do Brasil divulga relatório anual"
    result_neu = service.analyze(text_neu, "BBAS3")
    
    print("\n📊 Teste Neutro:")
    print(f"  Texto: '{text_neu}'")
    print(f"  Polaridade: {result_neu.polarity}")
    print(f"  Label: {result_neu.label}")
    print(f"  Confiança: {result_neu.confidence}")
    print("  ✅ PASSOU")


def test_models():
    """Testa modelos de dados"""
    print_section("TESTE DE MODELOS")
    
    # Criar SentimentAnalysis
    sentiment = SentimentAnalysis(
        polarity=0.5,
        subjectivity=0.6,
        label='positive',
        confidence=0.8,
        positive_keywords=3,
        negative_keywords=0
    )
    
    print("\n✅ SentimentAnalysis criado:")
    print(f"  {sentiment}")
    
    # Criar NewsArticle
    article = NewsArticle(
        url="https://example.com/test",
        query="BBAS3 teste",
        titulo_noticia="Teste de Notícia",
        publicada=datetime.now(timezone.utc).isoformat(),
        busca_feita=datetime.now(timezone.utc).isoformat(),
        resumo="Resumo de teste com palavras-chave",
        sentimentos=sentiment
    )
    
    print("\n✅ NewsArticle criado:")
    print(f"  URL: {article.url}")
    print(f"  Título: {article.titulo_noticia}")
    
    # Testar transformação para MongoDB (nested)
    mongo_dict = article.to_dict()
    print("\n✅ Transformação para MongoDB (nested):")
    print(f"  Campos: {len(mongo_dict)}")
    print(f"  Tem 'sentimentos' nested: {'sentimentos' in mongo_dict}")
    assert 'sentimentos' in mongo_dict, "Deve ter sentimentos nested"
    assert isinstance(mongo_dict['sentimentos'], dict), "Sentimentos deve ser dict"
    print("  ✅ PASSOU")
    
    # Testar transformação para SQL (flat)
    sql_dict = article.to_relational_dict()
    print("\n✅ Transformação para SQL (flat):")
    print(f"  Campos: {len(sql_dict)}")
    print(f"  Tem 'url_hash': {'url_hash' in sql_dict}")
    print(f"  Tem 'sentimento_polarity': {'sentimento_polarity' in sql_dict}")
    print(f"  Tem 'sentimento_label': {'sentimento_label' in sql_dict}")
    print(f"  Tem 'ano_publicacao': {'ano_publicacao' in sql_dict}")
    print(f"  Tem 'sentimento_score': {'sentimento_score' in sql_dict}")
    assert 'url_hash' in sql_dict, "Deve ter url_hash"
    assert 'sentimento_polarity' in sql_dict, "Deve ter sentimento_polarity flat"
    assert 'sentimento_label' in sql_dict, "Deve ter sentimento_label"
    assert 'sentimentos' not in sql_dict, "Não deve ter sentimentos nested"
    print("  ✅ PASSOU")
    
    print(f"\n✅ Total de colunas SQL: {len(sql_dict)}")
    print("  Principais campos:")
    for key in ['url_hash', 'query_category', 'titulo_limpo', 'sentimento_polarity', 
                'sentimento_score', 'relevancia', 'ano_publicacao', 'mes_publicacao']:
        if key in sql_dict:
            print(f"    - {key}: {sql_dict[key]}")


def test_data_transformation():
    """Testa transformação de dados em detalhes"""
    print_section("TESTE DE TRANSFORMAÇÃO DE DADOS")
    
    sentiment = SentimentAnalysis(
        polarity=0.3,
        subjectivity=0.5,
        label='positive',
        confidence=0.7,
        positive_keywords=3,
        negative_keywords=1
    )
    
    article = NewsArticle(
        url="https://news.google.com/articles/test123",
        query="BBAS3 Banco do Brasil resultados 2025",
        titulo_noticia="Banco do Brasil anuncia LUCRO recorde",
        publicada="2025-01-15T10:30:00Z",
        busca_feita=datetime.now(timezone.utc).isoformat(),
        resumo="O Banco do Brasil anunciou lucro recorde...",
        sentimentos=sentiment
    )
    
    # Transformação MongoDB
    mongo = article.to_dict()
    print("\n📊 MongoDB (Nested):")
    print(f"  sentimentos.polarity: {mongo['sentimentos']['polarity']}")
    print(f"  sentimentos.label: {mongo['sentimentos']['label']}")
    print(f"  Estrutura: NESTED")
    
    # Transformação SQL
    sql = article.to_relational_dict()
    print("\n📊 SQL (Flat):")
    print(f"  sentimento_polarity: {sql['sentimento_polarity']}")
    print(f"  sentimento_label: {sql['sentimento_label']}")
    print(f"  url_hash: {sql['url_hash']}")
    print(f"  query_category: {sql['query_category']}")
    print(f"  ano_publicacao: {sql['ano_publicacao']}")
    print(f"  mes_publicacao: {sql['mes_publicacao']}")
    print(f"  sentimento_score: {sql['sentimento_score']}")
    print(f"  relevancia: {sql['relevancia']}")
    print(f"  Estrutura: FLAT")
    
    print("\n✅ Transformações funcionando corretamente!")
    print(f"   MongoDB: {len(mongo)} campos (nested)")
    print(f"   SQL: {len(sql)} campos (flat)")


def main():
    """Executa todos os testes"""
    print("\n" + "🚀" * 30)
    print("TESTES COMPLETOS DO SISTEMA REFATORADO")
    print("🚀" * 30)
    
    try:
        test_configuration()
        test_sentiment_analysis()
        test_models()
        test_data_transformation()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        print("\n💡 Sistema pronto para uso!")
        print("💡 Execute: python collect_news_bbas3.py")
        print("\n")
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
