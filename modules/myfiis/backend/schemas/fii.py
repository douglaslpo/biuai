"""
Schemas Pydantic para o módulo MyFIIs
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class FIIBase(BaseModel):
    """Schema base para FII"""
    codigo: str = Field(..., min_length=4, max_length=10)
    nome: str = Field(..., min_length=2, max_length=100)
    segmento: str = Field(..., min_length=2, max_length=50)
    
    # Dados financeiros
    preco_atual: float = Field(..., gt=0)
    dividend_yield: float = Field(..., ge=0)
    patrimonio_liquido: float = Field(..., gt=0)
    valor_patrimonial: float = Field(..., gt=0)
    liquidez_diaria: float = Field(..., ge=0)
    
    # Métricas
    rentabilidade_mes: Optional[float] = None
    rentabilidade_ano: Optional[float] = None
    rentabilidade_12m: Optional[float] = None
    
    # Dados adicionais
    quantidade_ativos: Optional[int] = None
    vacancia_media: Optional[float] = None

    class Config:
        orm_mode = True


class FIICreate(FIIBase):
    """Schema para criação de FII"""
    pass


class FIIUpdate(BaseModel):
    """Schema para atualização de FII"""
    nome: Optional[str] = None
    segmento: Optional[str] = None
    preco_atual: Optional[float] = None
    dividend_yield: Optional[float] = None
    patrimonio_liquido: Optional[float] = None
    valor_patrimonial: Optional[float] = None
    liquidez_diaria: Optional[float] = None
    rentabilidade_mes: Optional[float] = None
    rentabilidade_ano: Optional[float] = None
    rentabilidade_12m: Optional[float] = None
    quantidade_ativos: Optional[int] = None
    vacancia_media: Optional[float] = None

    class Config:
        orm_mode = True


class FII(FIIBase):
    """Schema completo de FII"""
    id: int
    created_at: datetime
    updated_at: datetime


class CarteiraFIIBase(BaseModel):
    """Schema base para carteira de FIIs"""
    fii_id: int
    quantidade: int = Field(..., gt=0)
    preco_medio: float = Field(..., gt=0)
    data_compra: datetime
    favorito: Optional[bool] = False
    alerta_ativo: Optional[bool] = False
    preco_alerta: Optional[float] = None

    class Config:
        orm_mode = True


class CarteiraFIICreate(CarteiraFIIBase):
    """Schema para criação de carteira"""
    pass


class CarteiraFIIUpdate(BaseModel):
    """Schema para atualização de carteira"""
    quantidade: Optional[int] = None
    preco_medio: Optional[float] = None
    favorito: Optional[bool] = None
    alerta_ativo: Optional[bool] = None
    preco_alerta: Optional[float] = None

    class Config:
        orm_mode = True


class CarteiraFII(CarteiraFIIBase):
    """Schema completo de carteira"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    fii: FII


class AnaliseFIIBase(BaseModel):
    """Schema base para análise de FII"""
    fii_id: int
    tendencia: Optional[str] = Field(None, regex="^(ALTA|BAIXA|LATERAL)$")
    rsi: Optional[float] = Field(None, ge=0, le=100)
    suporte: Optional[float] = None
    resistencia: Optional[float] = None
    score_liquidez: Optional[float] = Field(None, ge=0, le=100)
    score_rentabilidade: Optional[float] = Field(None, ge=0, le=100)
    score_risco: Optional[float] = Field(None, ge=0, le=100)
    score_geral: Optional[float] = Field(None, ge=0, le=100)
    recomendacao: Optional[str] = Field(None, regex="^(COMPRAR|VENDER|MANTER)$")
    confianca: Optional[float] = Field(None, ge=0, le=1)
    explicacao: Optional[str] = Field(None, max_length=500)

    class Config:
        orm_mode = True


class AnaliseFIICreate(AnaliseFIIBase):
    """Schema para criação de análise"""
    pass


class AnaliseFIIUpdate(BaseModel):
    """Schema para atualização de análise"""
    tendencia: Optional[str] = None
    rsi: Optional[float] = None
    suporte: Optional[float] = None
    resistencia: Optional[float] = None
    score_liquidez: Optional[float] = None
    score_rentabilidade: Optional[float] = None
    score_risco: Optional[float] = None
    score_geral: Optional[float] = None
    recomendacao: Optional[str] = None
    confianca: Optional[float] = None
    explicacao: Optional[str] = None

    class Config:
        orm_mode = True


class AnaliseFII(AnaliseFIIBase):
    """Schema completo de análise"""
    id: int
    created_at: datetime
    updated_at: datetime
    fii: FII 