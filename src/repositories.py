"""
Repositórios para acesso a dados
Implementa padrão Repository para desacoplar lógica de negócio do acesso a dados
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import logging
from pymongo import MongoClient, errors
from sqlalchemy import create_engine, text
import pandas as pd
from snowflake.connector import connect
from snowflake.connector.pandas_tools import write_pandas

from src.models import NewsArticle
from src.config import MongoDBConfig, PostgreSQLConfig, SnowflakeConfig

logger = logging.getLogger(__name__)


class INewsRepository(ABC):
    """Interface para repositório de notícias"""
    
    @abstractmethod
    def save(self, articles: List[NewsArticle]) -> int:
        """Salva artigos e retorna quantidade salva"""
        pass
    
    @abstractmethod
    def find_by_url(self, url: str) -> Optional[NewsArticle]:
        """Busca artigo por URL"""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Conta total de artigos"""
        pass


class MongoDBRepository(INewsRepository):
    """Repositório MongoDB"""
    
    def __init__(self, config: MongoDBConfig):
        self.config = config
        self._client = None
        self._collection = None

    def _connect(self):
        """Estabelece conexão com MongoDB"""
        if self._collection is None:
            try:
                self._client = MongoClient(
                    self.config.uri,
                    serverSelectionTimeoutMS=5000
                )
                self._client.admin.command('ping')
                db = self._client[self.config.database]
                self._collection = db[self.config.collection]
                logger.info(f"✅ Conectado ao MongoDB: {self.config.database}.{self.config.collection}")
            except errors.ServerSelectionTimeoutError as e:
                logger.error(f"❌ Erro ao conectar ao MongoDB: {e}")
                raise

    def save(self, articles: List[NewsArticle]) -> int:
        """Salva artigos no MongoDB usando upsert"""
        self._connect()
        
        saved_count = 0
        for article in articles:
            try:
                result = self._collection.update_one(
                    {'url': article.url},
                    {'$set': article.to_dict()},
                    upsert=True
                )
                if result.upserted_id or result.modified_count > 0:
                    saved_count += 1
            except Exception as e:
                logger.error(f"Erro ao salvar artigo {article.url}: {e}")
        
        logger.info(f"✅ MongoDB: {saved_count} documentos salvos/atualizados")
        return saved_count

    def find_by_url(self, url: str) -> Optional[NewsArticle]:
        """Busca artigo por URL"""
        self._connect()
        doc = self._collection.find_one({'url': url})
        return NewsArticle.from_dict(doc) if doc else None

    def count(self) -> int:
        """Conta total de artigos"""
        self._connect()
        return self._collection.count_documents({})

    def close(self):
        """Fecha conexão"""
        if self._client:
            self._client.close()


class PostgreSQLRepository(INewsRepository):
    """Repositório PostgreSQL"""
    
    def __init__(self, config: PostgreSQLConfig):
        self.config = config
        self._engine = None
        self.table_name = 'noticias_bbas3'

    def _connect(self):
        """Estabelece conexão com PostgreSQL"""
        if self._engine is None:
            try:
                self._engine = create_engine(
                    self.config.get_connection_string(),
                    pool_pre_ping=True
                )
                # Testa conexão
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info(f"✅ Conectado ao PostgreSQL: {self.config.database}")
            except Exception as e:
                logger.error(f"❌ Erro ao conectar ao PostgreSQL: {e}")
                raise

    def save(self, articles: List[NewsArticle]) -> int:
        """Salva artigos no PostgreSQL"""
        self._connect()
        
        try:
            # Converte para formato relacional
            records = [article.to_relational_dict() for article in articles]
            df = pd.DataFrame(records)
            
            # Remove duplicatas pelo hash da URL
            df = df.drop_duplicates(subset=['url_hash'], keep='last')
            
            # Salva no banco (substitui tabela)
            df.to_sql(
                self.table_name,
                self._engine,
                if_exists='replace',
                index=False,
                method='multi'
            )
            
            saved_count = len(df)
            logger.info(f"✅ PostgreSQL: {saved_count} registros salvos na tabela '{self.table_name}'")
            return saved_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar no PostgreSQL: {e}")
            raise

    def find_by_url(self, url: str) -> Optional[NewsArticle]:
        """Busca artigo por URL"""
        self._connect()
        
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        query = f"SELECT * FROM {self.table_name} WHERE url_hash = :url_hash"
        
        with self._engine.connect() as conn:
            result = conn.execute(text(query), {'url_hash': url_hash})
            row = result.fetchone()
            
        # Nota: Retorna None pois formato relacional é diferente
        # Para reconstruir NewsArticle seria necessário reverter transformações
        return None

    def count(self) -> int:
        """Conta total de artigos"""
        self._connect()
        
        query = f"SELECT COUNT(*) as total FROM {self.table_name}"
        
        with self._engine.connect() as conn:
            result = conn.execute(text(query))
            row = result.fetchone()
            return row[0] if row else 0


class SnowflakeRepository(INewsRepository):
    """Repositório Snowflake"""
    
    def __init__(self, config: SnowflakeConfig):
        self.config = config
        self.table_name = 'NOTICIAS_BBAS3'

    def _connect(self):
        """Cria conexão com Snowflake"""
        try:
            conn = connect(
                user=self.config.user,
                password=self.config.password,
                account=self.config.account,
                warehouse=self.config.warehouse,
                database=self.config.database,
                schema=self.config.schema
            )
            logger.info(f"✅ Conectado ao Snowflake: {self.config.database}.{self.config.schema}")
            return conn
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao Snowflake: {e}")
            raise

    def save(self, articles: List[NewsArticle]) -> int:
        """Salva artigos no Snowflake"""
        conn = self._connect()
        
        try:
            # Converte para formato relacional
            records = [article.to_relational_dict() for article in articles]
            df = pd.DataFrame(records)
            
            # Remove duplicatas pelo hash da URL
            df = df.drop_duplicates(subset=['url_hash'], keep='last')
            
            # Converte colunas de data para formato compatível
            date_columns = ['publicada', 'busca_feita']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Salva no Snowflake
            success, nchunks, nrows, _ = write_pandas(
                conn=conn,
                df=df,
                table_name=self.table_name,
                auto_create_table=True,
                overwrite=True,
                quote_identifiers=False
            )
            
            conn.close()
            
            if success:
                logger.info(f"✅ Snowflake: {nrows} registros salvos na tabela '{self.table_name}'")
                return nrows
            else:
                logger.error("❌ Erro ao salvar no Snowflake")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar no Snowflake: {e}")
            if conn:
                conn.close()
            raise

    def find_by_url(self, url: str) -> Optional[NewsArticle]:
        """Busca artigo por URL"""
        # Não implementado para Snowflake (apenas leitura analítica)
        return None

    def count(self) -> int:
        """Conta total de artigos"""
        conn = self._connect()
        
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Erro ao contar registros: {e}")
            if conn:
                conn.close()
            return 0
