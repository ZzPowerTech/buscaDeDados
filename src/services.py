"""
Serviços de negócio
Implementa a lógica principal da aplicação
"""
import logging
import random
import time
from urllib.parse import quote_plus
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

import feedparser
from textblob import TextBlob

from src.models import NewsArticle, SentimentAnalysis
from src.repositories import INewsRepository

logger = logging.getLogger(__name__)


class SentimentAnalysisService:
    """Serviço de análise de sentimento"""
    
    # Palavras-chave financeiras positivas (português)
    POSITIVE_KEYWORDS = [
        'lucro', 'crescimento', 'alta', 'valorização', 'recuperação', 'expansão',
        'positivo', 'aumento', 'ganho', 'melhora', 'sucesso', 'recorde', 'superação',
        'dividendos', 'rentabilidade', 'eficiência', 'otimista', 'sólido'
    ]
    
    # Palavras-chave financeiras negativas (português)
    NEGATIVE_KEYWORDS = [
        'prejuízo', 'queda', 'desvalorização', 'crise', 'inadimplência', 'calote',
        'negativo', 'perda', 'declínio', 'deterioração', 'sanção', 'multa',
        'default', 'provisão', 'risco', 'pessimista', 'fraco', 'inadimplente'
    ]
    
    def analyze(self, text: str, title: str = "") -> SentimentAnalysis:
        """
        Analisa sentimento de texto com contexto financeiro
        
        Args:
            text: Texto principal para análise
            title: Título (opcional, aumenta contexto)
            
        Returns:
            SentimentAnalysis: Objeto com análise completa
        """
        if not text:
            return SentimentAnalysis(
                polarity=0.0,
                subjectivity=0.0,
                label='neutral',
                confidence=0.0,
                positive_keywords=0,
                negative_keywords=0
            )
        
        # Combina título e texto para melhor contexto
        full_text = f"{title} {text}" if title else text
        
        # Análise com TextBlob
        blob = TextBlob(full_text)
        base_polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Conta keywords financeiras
        text_lower = full_text.lower()
        pos_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in text_lower)
        neg_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text_lower)
        
        # Ajusta polaridade com keywords (peso 0.15 por keyword)
        keyword_adjustment = (pos_count - neg_count) * 0.15
        adjusted_polarity = base_polarity + keyword_adjustment
        
        # Limita entre -1 e 1
        adjusted_polarity = max(-1.0, min(1.0, adjusted_polarity))
        
        # Define label com threshold de ±0.05
        if adjusted_polarity > 0.05:
            label = 'positive'
        elif adjusted_polarity < -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        # Calcula confiança (maior com mais keywords e polaridade forte)
        confidence = min(1.0, (
            abs(adjusted_polarity) + 
            (pos_count + neg_count) * 0.1 + 
            subjectivity
        ) / 2)
        
        return SentimentAnalysis(
            polarity=round(adjusted_polarity, 4),
            subjectivity=round(subjectivity, 4),
            label=label,
            confidence=round(confidence, 4),
            positive_keywords=pos_count,
            negative_keywords=neg_count
        )


class NewsCollectorService:
    """Serviço de coleta de notícias"""
    
    def __init__(
        self,
        sentiment_service: SentimentAnalysisService,
        max_per_query: int = 100,
        max_years_back: int = 5,
        sleep_between: float = 1.0
    ):
        self.sentiment_service = sentiment_service
        self.max_per_query = max_per_query
        self.max_years_back = max_years_back
        self.sleep_between = sleep_between

    def collect_from_query(self, query: str) -> List[NewsArticle]:
        """
        Coleta notícias de uma query específica
        
        Args:
            query: String de busca
            
        Returns:
            List[NewsArticle]: Lista de artigos coletados
        """
        logger.info(f"📰 Buscando: {query}")
        
        # Constrói URL do RSS
        feed_url = self._build_rss_url(query)
        
        # Faz parse do feed
        feed = feedparser.parse(feed_url)
        
        if getattr(feed, 'bozo', False):
            logger.warning(f"⚠️  Erro ao processar RSS: {feed.get('bozo_exception', 'Desconhecido')}")
        
        entries = feed.get('entries', [])[:self.max_per_query]
        articles = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=365 * self.max_years_back)
        
        for entry in entries:
            # Verifica data de publicação
            pub_date = self._extract_publication_date(entry)
            if pub_date and pub_date < cutoff_date:
                continue
            
            # Cria artigo
            article = self._create_article_from_entry(entry, query)
            if article:
                articles.append(article)
            
            # Respeita rate limit
            time.sleep(self.sleep_between + random.random() * 0.5)
        
        logger.info(f"✅ Coletados {len(articles)} artigos para query: {query}")
        return articles

    def _build_rss_url(self, query: str) -> str:
        """Constrói URL do Google News RSS"""
        encoded_query = quote_plus(query)
        return f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

    def _extract_publication_date(self, entry: Dict[str, Any]) -> datetime:
        """Extrai data de publicação do entry"""
        if 'published_parsed' in entry and entry.published_parsed:
            try:
                return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            except:
                pass
        return None

    def _extract_text_from_entry(self, entry: Dict[str, Any]) -> str:
        """Extrai texto do entry (summary ou content)"""
        # Tenta content primeiro
        if 'content' in entry and len(entry.content) > 0:
            content_parts = [c.value for c in entry.content if hasattr(c, 'value')]
            if content_parts:
                return ' '.join(content_parts)
        
        # Fallback para summary
        return entry.get('summary', '')

    def _create_snippet(self, text: str, max_words: int = 25) -> str:
        """Cria snippet do texto"""
        if not text:
            return ""
        
        # Separa por parágrafos
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        
        # Procura parágrafo com pelo menos 5 palavras
        for para in paragraphs:
            words = para.split()
            if len(words) >= 5:
                snippet = " ".join(words[:max_words])
                suffix = "..." if len(words) > max_words else ""
                return snippet.rstrip(" .,:;") + suffix
        
        # Fallback: primeiro parágrafo
        if paragraphs:
            words = paragraphs[0].split()
            snippet = " ".join(words[:max_words])
            return snippet.rstrip(" .,:;") + "..."
        
        return ""

    def _create_article_from_entry(self, entry: Dict[str, Any], query: str) -> NewsArticle:
        """Cria NewsArticle a partir de entry do RSS"""
        url = entry.get('link', '')
        if not url:
            return None
        
        title = entry.get('title', '')
        text = self._extract_text_from_entry(entry)
        full_text = text or title
        
        # Gera snippet
        snippet = self._create_snippet(full_text)
        
        # Analisa sentimento
        sentiment = self.sentiment_service.analyze(full_text, title)
        
        # Extrai data de publicação
        pub_date = self._extract_publication_date(entry)
        pub_date_iso = pub_date.isoformat() if pub_date else None
        
        return NewsArticle(
            url=url,
            query=query,
            titulo_noticia=title,
            publicada=pub_date_iso,
            busca_feita=datetime.now(timezone.utc).isoformat(),
            resumo=snippet,
            sentimentos=sentiment
        )


class NewsPersistenceService:
    """Serviço de persistência de notícias"""
    
    def __init__(self, repositories: List[INewsRepository]):
        self.repositories = repositories

    def save_all(self, articles: List[NewsArticle]) -> Dict[str, int]:
        """
        Salva artigos em todos os repositórios configurados
        
        Returns:
            Dict com nome do repositório e quantidade salva
        """
        results = {}
        
        for repo in self.repositories:
            repo_name = repo.__class__.__name__.replace('Repository', '')
            try:
                count = repo.save(articles)
                results[repo_name] = count
            except Exception as e:
                logger.error(f"❌ Erro ao salvar em {repo_name}: {e}")
                results[repo_name] = 0
        
        return results
