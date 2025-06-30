from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class TipoLancamento(str, enum.Enum):
    RECEITA = "RECEITA"
    DESPESA = "DESPESA"

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
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class MetaFinanceira(Base):
    __tablename__ = "metas_financeiras"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String)
    valor_meta = Column(Float)
    valor_atual = Column(Float)
    data_inicio = Column(DateTime(timezone=True))
    data_fim = Column(DateTime(timezone=True))
    user_id = Column(Integer, ForeignKey("users.id"))
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 