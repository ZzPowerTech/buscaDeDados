"""
Coleta notícias do Google News RSS sobre BBAS3/Banco do Brasil
com análise de sentimento e armazenamento multi-database.

Arquitetura SOLID/Clean Code
Usa variáveis de ambiente (.env)
"""

import json
import logging
from typing import List

from src.config import settings
from src.models import NewsArticle
from src.services import (
    SentimentAnalysisService,
    NewsCollectorService,
    NewsPersistenceService
)
from src.repositories import (
    MongoDBRepository,
    PostgreSQLRepository,
    SnowflakeRepository
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Queries de busca
QUERIES = [
    "BBAS3 Banco do Brasil resultados 2025",
    "Banco do Brasil agribusiness inadimplencia 2025",
    "OFAC sanctions Brazil Banco do Brasil",
    "Magnitsky act Brazil Banco do Brasil",
    "Banco do Brasil",
    "BBAS3 B3",
    "BBAS3 Banco do Brasil resultados 2024",
    "Banco do Brasil agribusiness inadimplencia 2024",
    "BBAS3 Banco do Brasil resultados 2023",
    "Banco do Brasil agribusiness inadimplencia 2023",
    "BBAS3 Banco do Brasil resultados 2022",
    "Banco do Brasil agribusiness inadimplencia 2022",
    "BBAS3 Banco do Brasil resultados 2021",
    "Banco do Brasil agribusiness inadimplencia 2021",
    "BBAS3 Banco do Brasil resultados 2020",
    "Banco do Brasil agribusiness inadimplencia 2020",
]


def save_json_local(articles: List[NewsArticle], filename: str):
    """Salva artigos em arquivo JSON local"""
    data = [article.to_dict() for article in articles]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ JSON salvo: {filename}")


def main():
    """Função principal de execução"""
    logger.info("="*60)
    logger.info("🚀 INICIANDO COLETA DE NOTÍCIAS BBAS3")
    logger.info("="*60)
    
    # Inicializa serviços
    sentiment_service = SentimentAnalysisService()
    
    collector = NewsCollectorService(
        sentiment_service=sentiment_service,
        max_per_query=settings.app.max_articles_per_query,
        max_years_back=settings.app.max_years_back,
        sleep_between=settings.app.sleep_between_requests
    )
    
    # Inicializa repositórios
    repositories = []
    
    if settings.mongodb.enabled:
        repositories.append(MongoDBRepository(
            config=settings.mongodb
        ))
    
    if settings.postgresql.enabled:
        repositories.append(PostgreSQLRepository(
            config=settings.postgresql
        ))
    
    if settings.snowflake.enabled:
        repositories.append(SnowflakeRepository(
            config=settings.snowflake
        ))
    
    persistence = NewsPersistenceService(repositories)
    
    # Coleta notícias de todas as queries
    all_articles = []
    seen_urls = set()
    
    for query in QUERIES:
        try:
            articles = collector.collect_from_query(query)
            
            # Remove duplicatas por URL
            for article in articles:
                if article.url not in seen_urls:
                    seen_urls.add(article.url)
                    all_articles.append(article)
        
        except Exception as e:
            logger.error(f"❌ Erro ao coletar query '{query}': {e}")
    
    logger.info(f"\n📊 Total de artigos únicos coletados: {len(all_articles)}")
    
    # Salva JSON local
    if settings.app.save_json_local:
        logger.info("\n" + "="*60)
        logger.info("💾 SALVANDO JSON LOCAL")
        logger.info("="*60)
        save_json_local(all_articles, settings.app.json_output_file)
    
    # Salva em bancos de dados
    if repositories:
        logger.info("\n" + "="*60)
        logger.info("💾 SALVANDO EM BANCOS DE DADOS")
        logger.info("="*60)
        
        results = persistence.save_all(all_articles)
        
        for repo_name, count in results.items():
            status = "✅" if count > 0 else "❌"
            logger.info(f"{status} {repo_name}: {count} artigos salvos")
    
    # Resumo final
    logger.info("\n" + "="*60)
    logger.info("✅ COLETA FINALIZADA COM SUCESSO!")
    logger.info("="*60)
    logger.info(f"📊 Total de notícias: {len(all_articles)}")
    
    if settings.mongodb.enabled:
        logger.info(f"💾 MongoDB: {settings.mongodb.database}.{settings.mongodb.collection}")
    
    if settings.postgresql.enabled:
        logger.info(f"💾 PostgreSQL: {settings.postgresql.database}.{settings.postgresql.table_name}")
    
    if settings.snowflake.enabled:
        logger.info(f"💾 Snowflake: {settings.snowflake.database}.{settings.snowflake.schema}.{settings.snowflake.table_name}")
    
    if settings.app.save_json_local:
        logger.info(f"📄 JSON: {settings.app.json_output_file}")
    
    logger.info("="*60)


if __name__ == "__main__":
    main()
