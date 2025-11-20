"""
Modelos de dados do projeto
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
import re


@dataclass
class SentimentAnalysis:
    """Modelo de análise de sentimento"""
    polarity: float
    subjectivity: float
    label: str
    confidence: float
    positive_keywords: int
    negative_keywords: int

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SentimentAnalysis':
        """Cria instância a partir de dicionário"""
        return cls(
            polarity=float(data.get('polarity', 0.0)),
            subjectivity=float(data.get('subjectivity', 0.0)),
            label=str(data.get('label', 'neutral')),
            confidence=float(data.get('confidence', 0.0)),
            positive_keywords=int(data.get('positive_keywords', 0)),
            negative_keywords=int(data.get('negative_keywords', 0))
        )


@dataclass
class NewsArticle:
    """Modelo de artigo de notícia"""
    url: str
    query: str
    titulo_noticia: str
    publicada: Optional[str]
    busca_feita: str
    resumo: str
    sentimentos: SentimentAnalysis

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário (MongoDB)"""
        return {
            'url': self.url,
            'query': self.query,
            'titulo_noticia': self.titulo_noticia,
            'publicada': self.publicada,
            'busca_feita': self.busca_feita,
            'resumo': self.resumo,
            'sentimentos': self.sentimentos.to_dict()
        }

    def to_relational_dict(self) -> Dict[str, Any]:
        """
        Converte para formato relacional (PostgreSQL/Snowflake)
        Expande sentimentos em colunas separadas e limpa dados
        """
        return {
            # Identificação
            'url': self._clean_text(self.url),
            'url_hash': self._generate_url_hash(self.url),
            
            # Metadados da busca
            'query': self._clean_text(self.query),
            'query_category': self._categorize_query(self.query),
            
            # Conteúdo
            'titulo_noticia': self._clean_text(self.titulo_noticia),
            'titulo_limpo': self._extract_clean_title(self.titulo_noticia),
            'fonte_noticia': self._extract_source(self.titulo_noticia),
            'resumo': self._clean_text(self.resumo),
            
            # Datas (formato ISO 8601 para compatibilidade)
            'publicada': self._parse_date(self.publicada),
            'busca_feita': self._parse_date(self.busca_feita),
            'ano_publicacao': self._extract_year(self.publicada),
            'mes_publicacao': self._extract_month(self.publicada),
            
            # Análise de Sentimento (expandido)
            'sentimento_label': self.sentimentos.label,
            'sentimento_polarity': round(self.sentimentos.polarity, 4),
            'sentimento_subjectivity': round(self.sentimentos.subjectivity, 4),
            'sentimento_confidence': round(self.sentimentos.confidence, 4),
            'sentimento_positive_keywords': self.sentimentos.positive_keywords,
            'sentimento_negative_keywords': self.sentimentos.negative_keywords,
            
            # Métricas derivadas
            'sentimento_score': self._calculate_sentiment_score(),
            'relevancia': self._calculate_relevance()
        }

    @staticmethod
    def _clean_text(text: Optional[str]) -> str:
        """Remove caracteres problemáticos e normaliza texto"""
        if not text:
            return ''
        # Remove quebras de linha, tabs e espaços múltiplos
        cleaned = re.sub(r'\s+', ' ', str(text))
        # Remove caracteres de controle
        cleaned = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', cleaned)
        return cleaned.strip()

    @staticmethod
    def _generate_url_hash(url: str) -> str:
        """Gera hash da URL para uso como chave única"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()

    @staticmethod
    def _categorize_query(query: str) -> str:
        """Categoriza a query de busca"""
        query_lower = query.lower()
        if 'inadimplencia' in query_lower or 'agribusiness' in query_lower:
            return 'INADIMPLENCIA_AGRO'
        elif 'resultados' in query_lower:
            return 'RESULTADOS_FINANCEIROS'
        elif 'ofac' in query_lower or 'magnitsky' in query_lower:
            return 'SANCOES_INTERNACIONAIS'
        elif 'b3' in query_lower:
            return 'MERCADO_ACOES'
        else:
            return 'GERAL'

    @staticmethod
    def _extract_clean_title(title: str) -> str:
        """Extrai título limpo sem fonte"""
        if not title:
            return ''
        # Remove fonte após " - "
        parts = title.split(' - ')
        return parts[0].strip() if parts else title.strip()

    @staticmethod
    def _extract_source(title: str) -> str:
        """Extrai fonte da notícia do título"""
        if not title or ' - ' not in title:
            return 'Desconhecido'
        parts = title.split(' - ')
        return parts[-1].strip() if len(parts) > 1 else 'Desconhecido'

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[str]:
        """Converte data para formato ISO 8601"""
        if not date_str:
            return None
        try:
            # Já está em formato ISO
            if 'T' in date_str:
                return date_str
            # Tenta parsear e converter
            from dateutil import parser
            dt = parser.parse(date_str)
            return dt.isoformat()
        except:
            return None

    @staticmethod
    def _extract_year(date_str: Optional[str]) -> Optional[int]:
        """Extrai ano da data"""
        if not date_str:
            return None
        try:
            from dateutil import parser
            dt = parser.parse(date_str)
            return dt.year
        except:
            return None

    @staticmethod
    def _extract_month(date_str: Optional[str]) -> Optional[int]:
        """Extrai mês da data"""
        if not date_str:
            return None
        try:
            from dateutil import parser
            dt = parser.parse(date_str)
            return dt.month
        except:
            return None

    def _calculate_sentiment_score(self) -> float:
        """
        Calcula score de sentimento normalizado (-1 a 1)
        Combina polaridade com keywords
        """
        keyword_score = (
            self.sentimentos.positive_keywords - 
            self.sentimentos.negative_keywords
        ) * 0.1
        
        combined_score = self.sentimentos.polarity + keyword_score
        # Limita entre -1 e 1
        return round(max(-1.0, min(1.0, combined_score)), 4)

    def _calculate_relevance(self) -> float:
        """
        Calcula relevância do artigo (0 a 1)
        Baseado em confiança, subjetividade e keywords
        """
        keyword_count = (
            self.sentimentos.positive_keywords + 
            self.sentimentos.negative_keywords
        )
        
        relevance = (
            self.sentimentos.confidence * 0.5 +
            (1 - self.sentimentos.subjectivity) * 0.3 +
            min(keyword_count / 10, 1.0) * 0.2
        )
        
        return round(relevance, 4)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NewsArticle':
        """Cria instância a partir de dicionário"""
        sentiment_data = data.get('sentimentos', {})
        
        return cls(
            url=data.get('url', ''),
            query=data.get('query', ''),
            titulo_noticia=data.get('titulo_noticia', ''),
            publicada=data.get('publicada'),
            busca_feita=data.get('busca_feita', datetime.now().isoformat()),
            resumo=data.get('resumo', ''),
            sentimentos=SentimentAnalysis.from_dict(sentiment_data)
        )
