"""
Schemas para funcionalidades de memória MCP
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class MemoriaCreate(BaseModel):
    """Schema para criação de memória"""
    content: str = Field(..., description="Conteúdo da memória")
    user_id: str = Field(..., description="ID do usuário")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")
    
    class Config:
        schema_extra = {
            "example": {
                "content": "Usuário preferiu investimentos de baixo risco",
                "user_id": "user123",
                "metadata": {
                    "categoria": "preferencias",
                    "contexto": "dashboard_financeiro"
                }
            }
        }


class MemoriaSearch(BaseModel):
    """Schema para busca de memórias"""
    query: str = Field(..., description="Consulta de busca")
    user_id: str = Field(..., description="ID do usuário")
    limit: Optional[int] = Field(10, description="Limite de resultados")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "investimentos",
                "user_id": "user123",
                "limit": 10
            }
        }


class MemoriaUpdate(BaseModel):
    """Schema para atualização de memória"""
    content: str = Field(..., description="Novo conteúdo da memória")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados atualizados")
    
    class Config:
        schema_extra = {
            "example": {
                "content": "Usuário mudou para investimentos de médio risco",
                "metadata": {
                    "categoria": "preferencias",
                    "contexto": "dashboard_financeiro",
                    "atualizado_em": "2024-01-15"
                }
            }
        }


class MemoriaResponse(BaseModel):
    """Schema de resposta para memória"""
    id: str = Field(..., description="ID único da memória")
    content: str = Field(..., description="Conteúdo da memória")
    metadata: Dict[str, Any] = Field(..., description="Metadados da memória")
    created_at: str = Field(..., description="Data de criação")
    updated_at: str = Field(..., description="Data de atualização")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "mem_123456",
                "content": "Usuário preferiu investimentos de baixo risco",
                "metadata": {
                    "categoria": "preferencias",
                    "contexto": "dashboard_financeiro"
                },
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class MemoriaSearchResult(BaseModel):
    """Schema para resultado de busca de memórias"""
    memories: List[MemoriaResponse] = Field(..., description="Lista de memórias encontradas")
    total: int = Field(..., description="Total de memórias encontradas")
    
    class Config:
        schema_extra = {
            "example": {
                "memories": [
                    {
                        "id": "mem_123456",
                        "content": "Usuário preferiu investimentos de baixo risco",
                        "metadata": {
                            "categoria": "preferencias",
                            "contexto": "dashboard_financeiro"
                        },
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total": 1
            }
        }


class MemoriaDeleteResponse(BaseModel):
    """Schema de resposta para deleção de memória"""
    message: str = Field(..., description="Mensagem de confirmação")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Memória deletada com sucesso"
            }
        } 