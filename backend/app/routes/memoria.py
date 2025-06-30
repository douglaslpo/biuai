"""
Rotas para funcionalidades de memória MCP
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer

from ..schemas.memoria import (
    MemoriaCreate,
    MemoriaSearch,
    MemoriaUpdate,
    MemoriaResponse,
    MemoriaSearchResult,
    MemoriaDeleteResponse
)
from ..services.memoria_service import memoria_service
from ..auth.jwt import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/memoria", tags=["Memória MCP"])
security = HTTPBearer()


@router.get("/health")
async def health_check():
    """Verificar saúde do serviço de memória"""
    try:
        result = await memoria_service.health_check()
        return result
    except Exception as e:
        logger.error(f"Erro no health check da memória: {e}")
        raise HTTPException(status_code=503, detail="Serviço de memória indisponível")


@router.post("/", response_model=MemoriaResponse)
async def criar_memoria(
    memoria: MemoriaCreate,
    current_user=Depends(get_current_user)
):
    """
    Criar uma nova memória no sistema MCP
    
    - **content**: Conteúdo da memória a ser armazenada
    - **user_id**: ID do usuário (pode ser diferente do usuário logado para contextos específicos)
    - **metadata**: Metadados opcionais para categorização
    """
    try:
        # Se não especificado, usar o ID do usuário logado
        user_id = memoria.user_id or str(current_user.id)
        
        result = await memoria_service.criar_memoria(
            content=memoria.content,
            user_id=user_id,
            metadata=memoria.metadata
        )
        
        logger.info(f"Memória criada para usuário {user_id}: {memoria.content[:50]}...")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao criar memória: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/search", response_model=MemoriaSearchResult)
async def buscar_memorias(
    query: str = Query(..., description="Consulta de busca"),
    user_id: Optional[str] = Query(None, description="ID do usuário (opcional)"),
    limit: int = Query(10, ge=1, le=100, description="Limite de resultados"),
    current_user=Depends(get_current_user)
):
    """
    Buscar memórias por consulta
    
    - **query**: Texto de busca nas memórias
    - **user_id**: ID do usuário (se não especificado, usa o usuário logado)
    - **limit**: Número máximo de resultados (1-100)
    """
    try:
        # Se não especificado, usar o ID do usuário logado
        target_user_id = user_id or str(current_user.id)
        
        result = await memoria_service.buscar_memorias(
            query=query,
            user_id=target_user_id,
            limit=limit
        )
        
        logger.info(f"Busca de memórias para usuário {target_user_id}: '{query}' - {result.get('total', 0)} resultados")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado na busca de memórias: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{user_id}", response_model=MemoriaSearchResult)
async def obter_memorias_usuario(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Limite de resultados"),
    current_user=Depends(get_current_user)
):
    """
    Obter todas as memórias de um usuário específico
    
    - **user_id**: ID do usuário
    - **limit**: Número máximo de resultados (1-1000)
    """
    try:
        # Verificar se o usuário pode acessar as memórias
        # Por segurança, só permite acesso às próprias memórias ou se for admin
        if str(current_user.id) != user_id and not getattr(current_user, 'is_admin', False):
            raise HTTPException(status_code=403, detail="Acesso negado às memórias deste usuário")
        
        result = await memoria_service.obter_memorias_usuario(
            user_id=user_id,
            limit=limit
        )
        
        logger.info(f"Obtidas {result.get('total', 0)} memórias para usuário {user_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao obter memórias do usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/{memory_id}", response_model=MemoriaResponse)
async def atualizar_memoria(
    memory_id: str,
    memoria: MemoriaUpdate,
    current_user=Depends(get_current_user)
):
    """
    Atualizar uma memória existente
    
    - **memory_id**: ID da memória a ser atualizada
    - **content**: Novo conteúdo da memória
    - **metadata**: Metadados atualizados (opcional)
    """
    try:
        result = await memoria_service.atualizar_memoria(
            memory_id=memory_id,
            content=memoria.content,
            metadata=memoria.metadata
        )
        
        logger.info(f"Memória {memory_id} atualizada por usuário {current_user.id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar memória: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/{memory_id}", response_model=MemoriaDeleteResponse)
async def deletar_memoria(
    memory_id: str,
    current_user=Depends(get_current_user)
):
    """
    Deletar uma memória
    
    - **memory_id**: ID da memória a ser deletada
    """
    try:
        result = await memoria_service.deletar_memoria(memory_id=memory_id)
        
        logger.info(f"Memória {memory_id} deletada por usuário {current_user.id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao deletar memória: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/")
async def listar_memorias_usuario_logado(
    limit: int = Query(50, ge=1, le=500, description="Limite de resultados"),
    current_user=Depends(get_current_user)
):
    """
    Obter memórias do usuário logado
    
    - **limit**: Número máximo de resultados (1-500)
    """
    try:
        result = await memoria_service.obter_memorias_usuario(
            user_id=str(current_user.id),
            limit=limit
        )
        
        logger.info(f"Listadas {result.get('total', 0)} memórias para usuário logado {current_user.id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao listar memórias do usuário logado: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 