"""
Serviço para integração com MCP Memory Service
"""

import logging
from typing import Dict, Any, List, Optional
import httpx
from fastapi import HTTPException

from ..core.config import settings

logger = logging.getLogger(__name__)


class MemoriaService:
    """Serviço para interação com o servidor MCP de memória"""
    
    def __init__(self):
        self.base_url = settings.MCP_MEMORY_SERVICE_URL
        self.timeout = float(settings.MCP_MEMORY_SERVICE_TIMEOUT)
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Fazer requisição HTTP para o serviço MCP"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Erro HTTP {e.response.status_code} ao acessar {url}: {e}")
                if e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail="Recurso não encontrado")
                elif e.response.status_code == 400:
                    raise HTTPException(status_code=400, detail="Dados inválidos")
                else:
                    raise HTTPException(status_code=500, detail="Erro interno do serviço de memória")
            except httpx.RequestError as e:
                logger.error(f"Erro de conexão com o serviço MCP: {e}")
                raise HTTPException(status_code=503, detail="Serviço de memória indisponível")
    
    async def criar_memoria(self, content: str, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Criar uma nova memória"""
        payload = {
            "content": content,
            "user_id": user_id
        }
        if metadata:
            payload["metadata"] = metadata
        
        return await self._make_request("POST", "/memories", json=payload)
    
    async def buscar_memorias(self, query: str, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Buscar memórias por consulta"""
        params = {
            "query": query,
            "user_id": user_id,
            "limit": limit
        }
        
        return await self._make_request("GET", "/memories/search", params=params)
    
    async def obter_memorias_usuario(self, user_id: str, limit: int = 100) -> Dict[str, Any]:
        """Obter todas as memórias de um usuário"""
        return await self._make_request("GET", f"/memories/{user_id}", params={"limit": limit})
    
    async def atualizar_memoria(self, memory_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Atualizar uma memória existente"""
        payload = {
            "memory_id": memory_id,
            "content": content
        }
        if metadata:
            payload["metadata"] = metadata
        
        return await self._make_request("PUT", f"/memories/{memory_id}", json=payload)
    
    async def deletar_memoria(self, memory_id: str) -> Dict[str, Any]:
        """Deletar uma memória"""
        return await self._make_request("DELETE", f"/memories/{memory_id}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar saúde do serviço MCP"""
        try:
            return await self._make_request("GET", "/health")
        except Exception as e:
            logger.error(f"Health check falhou: {e}")
            return {"status": "unhealthy", "error": str(e)}


# Instância global do serviço
memoria_service = MemoriaService() 