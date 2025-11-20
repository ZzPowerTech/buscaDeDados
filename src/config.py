"""
Configurações centralizadas do projeto.
Carrega variáveis de ambiente do arquivo .env
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()


@dataclass
class MongoDBConfig:
    """Configurações do MongoDB"""
    uri: str
    database: str
    collection: str
    enabled: bool = True

    @classmethod
    def from_env(cls) -> 'MongoDBConfig':
        return cls(
            uri=os.getenv('MONGO_URI', 'mongodb://localhost:27017/'),
            database=os.getenv('MONGO_DB', 'bigData'),
            collection=os.getenv('MONGO_COLLECTION', 'projeto_ativos'),
            enabled=os.getenv('MONGO_ENABLED', 'true').lower() == 'true'
        )


@dataclass
class PostgreSQLConfig:
    """Configurações do PostgreSQL"""
    user: str
    password: str
    host: str
    port: str
    database: str
    table_name: str = 'noticias_bbas3'
    enabled: bool = True

    @classmethod
    def from_env(cls) -> 'PostgreSQLConfig':
        return cls(
            user=os.getenv('PG_USER', 'postgres'),
            password=os.getenv('PG_PASSWORD', ''),
            host=os.getenv('PG_HOST', 'localhost'),
            port=os.getenv('PG_PORT', '5432'),
            database=os.getenv('PG_DB', 'bigdata'),
            table_name=os.getenv('PG_TABLE', 'noticias_bbas3'),
            enabled=os.getenv('PG_ENABLED', 'true').lower() == 'true'
        )

    def get_connection_string(self) -> str:
        """Retorna string de conexão SQLAlchemy"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class SnowflakeConfig:
    """Configurações do Snowflake"""
    user: str
    password: str
    account: str
    warehouse: str
    database: str
    schema: str
    table_name: str = 'NOTICIAS_BBAS3'
    enabled: bool = True

    @classmethod
    def from_env(cls) -> 'SnowflakeConfig':
        return cls(
            user=os.getenv('SF_USER', ''),
            password=os.getenv('SF_PASSWORD', ''),
            account=os.getenv('SF_ACCOUNT', ''),
            warehouse=os.getenv('SF_WAREHOUSE', 'COMPUTE_WH'),
            database=os.getenv('SF_DATABASE', 'BBAS3'),
            schema=os.getenv('SF_SCHEMA', 'PUBLIC'),
            table_name=os.getenv('SF_TABLE', 'NOTICIAS_BBAS3'),
            enabled=os.getenv('SF_ENABLED', 'true').lower() == 'true'
        )


@dataclass
class AppConfig:
    """Configurações gerais da aplicação"""
    max_articles_per_query: int
    max_years_back: int
    sleep_between_requests: float
    json_output_file: str
    log_level: str
    save_json_local: bool = True

    @classmethod
    def from_env(cls) -> 'AppConfig':
        return cls(
            max_articles_per_query=int(os.getenv('MAX_PER_QUERY', '100')),
            max_years_back=int(os.getenv('MAX_YEARS_BACK', '5')),
            sleep_between_requests=float(os.getenv('SLEEP_BETWEEN_REQUESTS', '1.0')),
            json_output_file=os.getenv('OUTPUT_JSON', 'data/collected_articles_bbas3.json'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            save_json_local=os.getenv('SAVE_JSON_LOCAL', 'true').lower() == 'true'
        )


class Settings:
    """Classe central de configurações"""
    
    def __init__(self):
        self.mongodb = MongoDBConfig.from_env()
        self.postgresql = PostgreSQLConfig.from_env()
        self.snowflake = SnowflakeConfig.from_env()
        self.app = AppConfig.from_env()
        
        # Queries de busca
        self.queries = [
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


# Instância global de configurações
settings = Settings()
