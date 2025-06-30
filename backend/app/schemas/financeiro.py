from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

class LancamentoBase(BaseModel):
    data: datetime
    valor: Decimal
    descricao: str
    tipo: str  # 'receita' ou 'despesa'
    categoria: str

class LancamentoCreate(LancamentoBase):
    pass

class LancamentoResponse(LancamentoBase):
    id: int
    usuario_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    total_receitas: Decimal
    total_despesas: Decimal
    saldo: Decimal
    lancamentos_por_categoria: dict
    historico_mensal: List[dict]

    class Config:
        from_attributes = True

# ==================== SCHEMAS DE CATEGORIAS ====================

class CategoriaBase(BaseModel):
    nome: str
    tipo: str  # 'RECEITA' ou 'DESPESA'
    descricao: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    descricao: Optional[str] = None

class CategoriaResponse(CategoriaBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 