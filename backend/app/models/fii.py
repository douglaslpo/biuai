from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.models.base import TenantModel

class FII(TenantModel):
    """Modelo para Fundos de Investimento Imobiliário"""
    
    # Informações básicas
    codigo = Column(String(10), index=True, nullable=False)
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
    
    # Configurações do usuário
    quantidade = Column(Integer, default=0, nullable=False)
    preco_medio = Column(Float, nullable=True)
    preco_alvo = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    favorito = Column(Boolean, default=False, nullable=False)
    notas = Column(String(500), nullable=True)
    
    # Alertas e notificações
    alertas = Column(JSON, default=[], nullable=False)
    ultima_notificacao = Column(DateTime, nullable=True)
    
    # Metadados
    ultima_atualizacao = Column(DateTime, nullable=True)
    ultima_analise = Column(DateTime, nullable=True)
    fii_metadata = Column(JSON, default={}, nullable=False)
    
    # Relacionamento com usuário (cada FII pertence a um usuário)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="fiis")

    # Relacionamentos
    analises = relationship("AnaliseFII", back_populates="fii", cascade="all, delete-orphan")
    transacoes = relationship("TransacaoFII", back_populates="fii", cascade="all, delete-orphan")
    
    class Config:
        orm_mode = True
    
    @property
    def valor_total(self) -> float:
        """Calcula valor total investido"""
        return self.quantidade * self.preco_medio if self.quantidade and self.preco_medio else 0
    
    @property
    def rentabilidade_total(self) -> Optional[float]:
        """Calcula rentabilidade total"""
        if not (self.quantidade and self.preco_medio and self.preco_atual):
            return None
        return ((self.preco_atual - self.preco_medio) / self.preco_medio) * 100
    
    @property
    def proventos_mensais(self) -> Optional[float]:
        """Calcula proventos mensais esperados"""
        if not (self.quantidade and self.preco_atual and self.dividend_yield):
            return None
        return (self.quantidade * self.preco_atual * self.dividend_yield) / 100 / 12
    
    def adicionar_alerta(self, tipo: str, valor: float, mensagem: str = None) -> None:
        """Adiciona um novo alerta"""
        self.alertas.append({
            'tipo': tipo,
            'valor': valor,
            'mensagem': mensagem,
            'criado_em': datetime.utcnow().isoformat()
        })
    
    def remover_alerta(self, tipo: str, valor: float) -> None:
        """Remove um alerta específico"""
        self.alertas = [
            a for a in self.alertas 
            if not (a['tipo'] == tipo and a['valor'] == valor)
        ]
    
    def get_fii_metadata(self, key: str, default: any = None) -> any:
        """Obtém um metadado"""
        return self.fii_metadata.get(key, default)
    
    def set_fii_metadata(self, key: str, value: any) -> None:
        """Define um metadado"""
        self.fii_metadata[key] = value

class AnaliseFII(TenantModel):
    """Modelo para análises de FIIs"""
    
    # Relacionamentos
    fii_id = Column(Integer, ForeignKey("fii.id"), nullable=False)
    fii = relationship("FII", back_populates="analises")
    
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
    
    # Dados adicionais
    dados_mercado = Column(JSON, default={}, nullable=False)
    metricas = Column(JSON, default={}, nullable=False)
    
    class Config:
        orm_mode = True

class TransacaoFII(TenantModel):
    """Modelo para transações de FIIs"""
    
    # Relacionamentos
    fii_id = Column(Integer, ForeignKey("fii.id"), nullable=False)
    fii = relationship("FII", back_populates="transacoes")
    
    # Dados da transação
    tipo = Column(String(10), nullable=False)  # COMPRA, VENDA
    data = Column(DateTime, nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco = Column(Float, nullable=False)
    
    # Custos
    corretagem = Column(Float, default=0, nullable=False)
    emolumentos = Column(Float, default=0, nullable=False)
    
    # Dados adicionais
    notas = Column(String(500), nullable=True)
    comprovante_url = Column(String(255), nullable=True)
    
    @property
    def valor_total(self) -> float:
        """Calcula valor total da transação"""
        return (self.quantidade * self.preco) + self.corretagem + self.emolumentos
    
    @property
    def preco_medio(self) -> float:
        """Calcula preço médio considerando custos"""
        return self.valor_total / self.quantidade if self.quantidade else 0
    
    class Config:
        orm_mode = True 