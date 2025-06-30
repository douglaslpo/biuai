from typing import Optional
from datetime import datetime
from pydantic import BaseModel, validator
from decimal import Decimal

from app.models.financeiro import TipoLancamento

class LancamentoBase(BaseModel):
    descricao: str
    valor: float
    tipo: TipoLancamento
    data_lancamento: datetime
    categoria_id: Optional[int] = None

class LancamentoCreate(LancamentoBase):
    @validator('valor')
    def valor_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser positivo')
        return v

class LancamentoUpdate(BaseModel):
    descricao: Optional[str] = None
    valor: Optional[float] = None
    tipo: Optional[TipoLancamento] = None
    data_lancamento: Optional[datetime] = None
    categoria_id: Optional[int] = None

    @validator('valor')
    def valor_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Valor deve ser positivo')
        return v

class LancamentoResponse(LancamentoBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LancamentoSummary(BaseModel):
    total_receitas: float
    total_despesas: float
    saldo: float
    total_lancamentos: int
    periodo_dias: int 