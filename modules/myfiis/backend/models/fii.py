"""
Modelos SQLAlchemy para o módulo MyFIIs
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.user import User


class FII(Base):
    """Modelo para Fundos de Investimento Imobiliário"""
    __tablename__ = "fiis"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), unique=True, index=True, nullable=False)
    nome = Column(String(100), nullable=False)
    segmento = Column(String(50), nullable=False)
    
    # Dados financeiros
    preco_atual = Column(Float, nullable=False)
    dividend_yield = Column(Float, nullable=False)
    patrimonio_liquido = Column(Float, nullable=False)
    valor_patrimonial = Column(Float, nullable=False)
    liquidez_diaria = Column(Float, nullable=False)
    
    # Métricas
    rentabilidade_mes = Column(Float)
    rentabilidade_ano = Column(Float)
    rentabilidade_12m = Column(Float)
    
    # Dados adicionais
    quantidade_ativos = Column(Integer)
    vacancia_media = Column(Float)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    carteiras = relationship("CarteiraFII", back_populates="fii")
    analises = relationship("AnaliseFII", back_populates="fii")


class CarteiraFII(Base):
    """Modelo para carteira de FIIs do usuário"""
    __tablename__ = "carteiras_fii"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fii_id = Column(Integer, ForeignKey("fiis.id"), nullable=False)
    
    quantidade = Column(Integer, nullable=False)
    preco_medio = Column(Float, nullable=False)
    data_compra = Column(DateTime, nullable=False)
    
    # Flags
    favorito = Column(Boolean, default=False)
    alerta_ativo = Column(Boolean, default=False)
    preco_alerta = Column(Float)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = relationship("User", back_populates="carteira_fiis")
    fii = relationship("FII", back_populates="carteiras")


class AnaliseFII(Base):
    """Modelo para análises de IA dos FIIs"""
    __tablename__ = "analises_fii"
    
    id = Column(Integer, primary_key=True, index=True)
    fii_id = Column(Integer, ForeignKey("fiis.id"), nullable=False)
    
    # Análise técnica
    tendencia = Column(String(20))  # ALTA, BAIXA, LATERAL
    rsi = Column(Float)
    suporte = Column(Float)
    resistencia = Column(Float)
    
    # Análise fundamentalista
    score_liquidez = Column(Float)
    score_rentabilidade = Column(Float)
    score_risco = Column(Float)
    score_geral = Column(Float)
    
    # Análise IA
    recomendacao = Column(String(20))  # COMPRAR, VENDER, MANTER
    confianca = Column(Float)  # 0-1
    explicacao = Column(String(500))
    
    # Embeddings para busca semântica
    embedding = Column(String)  # Vetor serializado
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    fii = relationship("FII", back_populates="analises") 