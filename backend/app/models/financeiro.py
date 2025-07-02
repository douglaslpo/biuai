from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class TipoLancamento(str, enum.Enum):
    RECEITA = "RECEITA"
    DESPESA = "DESPESA"

class StatusMeta(str, enum.Enum):
    ATIVA = "ATIVA"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"
    PAUSADA = "PAUSADA"

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
    tipo = Column(Enum(TipoLancamento))
    descricao = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    lancamentos = relationship("Lancamento", back_populates="categoria")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Conta(Base):
    __tablename__ = "contas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)  # Nome da conta (ex: "Conta Corrente", "Poupança")
    banco = Column(String)  # Nome do banco
    numero_conta = Column(String, nullable=True)  # Número da conta
    agencia = Column(String, nullable=True)  # Agência
    tipo_conta = Column(String, default="CORRENTE")  # CORRENTE, POUPANCA, INVESTIMENTO
    saldo_inicial = Column(Float, default=0.0)
    saldo_atual = Column(Float, default=0.0)
    ativa = Column(String, default="true")  # Para desativar contas sem deletar
    user_id = Column(Integer, ForeignKey("users.id"))
    
    lancamentos = relationship("Lancamento", back_populates="conta")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Lancamento(Base):
    __tablename__ = "lancamentos"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String)
    valor = Column(Float)
    tipo = Column(Enum(TipoLancamento))
    data_lancamento = Column(DateTime(timezone=True))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    categoria = relationship("Categoria", back_populates="lancamentos")
    
    conta_id = Column(Integer, ForeignKey("contas.id"), nullable=True)
    conta = relationship("Conta", back_populates="lancamentos")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class MetaFinanceira(Base):
    __tablename__ = "metas_financeiras"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    descricao = Column(String, nullable=True)
    valor_meta = Column(Float)
    valor_atual = Column(Float, default=0.0)
    data_inicio = Column(DateTime(timezone=True))
    data_fim = Column(DateTime(timezone=True))
    status = Column(Enum(StatusMeta), default=StatusMeta.ATIVA)
    user_id = Column(Integer, ForeignKey("users.id"))
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    
    # Relacionamento opcional com categoria
    categoria = relationship("Categoria")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 