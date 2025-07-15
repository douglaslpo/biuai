from pydantic import BaseModel, Field, validator
import re

class FIIBase(BaseModel):
    codigo: str = Field(..., min_length=6, max_length=10)
    nome: str = Field(..., min_length=1, max_length=255)
    segmento: str = Field(..., min_length=1, max_length=50)
    preco_atual: float = Field(..., gt=0)
    dividend_yield: float | None = Field(None, ge=0)
    patrimonio_liquido: float | None = Field(None, gt=0)
    valor_patrimonial: float | None = Field(None, gt=0)
    liquidez_diaria: float | None = Field(None, ge=0)

    @validator('codigo')
    def validate_codigo(cls, v):
        if not re.match(r'^[A-Z0-9]{4,6}11$', v):
            raise ValueError('Código de FII inválido')
        return v

class FIICreate(FIIBase):
    pass

class FIIUpdate(FIIBase):
    pass

class FII(FIIBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class FIIAnalytics(BaseModel):
    total_investido: float
    rendimento_mensal: float
    dy_medio: float
    total_fiis: int

    class Config:
        orm_mode = True 