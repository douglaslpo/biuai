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

# ==================== SCHEMAS DE METAS ====================

class MetaFinanceiraBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    valor_meta: float
    data_inicio: datetime
    data_fim: datetime
    categoria_id: Optional[int] = None

class MetaFinanceiraCreate(MetaFinanceiraBase):
    pass

class MetaFinanceiraUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    valor_meta: Optional[float] = None
    valor_atual: Optional[float] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    status: Optional[str] = None
    categoria_id: Optional[int] = None

class MetaFinanceiraResponse(MetaFinanceiraBase):
    id: int
    valor_atual: float
    status: str
    user_id: int
    categoria: Optional[CategoriaResponse] = None
    progresso_percentual: Optional[float] = None
    dias_restantes: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== SCHEMAS DE CONTAS ====================

class ContaBase(BaseModel):
    nome: str
    banco: str
    numero_conta: Optional[str] = None
    agencia: Optional[str] = None
    tipo_conta: str = "CORRENTE"  # CORRENTE, POUPANCA, INVESTIMENTO
    saldo_inicial: float = 0.0

class ContaCreate(ContaBase):
    pass

class ContaUpdate(BaseModel):
    nome: Optional[str] = None
    banco: Optional[str] = None
    numero_conta: Optional[str] = None
    agencia: Optional[str] = None
    tipo_conta: Optional[str] = None
    saldo_inicial: Optional[float] = None
    ativa: Optional[str] = None

class ContaResponse(ContaBase):
    id: int
    saldo_atual: float
    ativa: str
    user_id: int
    total_receitas: Optional[float] = None
    total_despesas: Optional[float] = None
    total_lancamentos: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== SCHEMAS DE RESUMOS ====================

class ResumoMetasResponse(BaseModel):
    total_metas: int
    metas_ativas: int
    metas_concluidas: int
    valor_total_metas: float
    valor_atual_total: float
    progresso_geral: float

class ResumoContasResponse(BaseModel):
    total_contas: int
    contas_ativas: int
    saldo_total: float
    maior_saldo: float
    menor_saldo: float
    banco_principal: Optional[str] = None 