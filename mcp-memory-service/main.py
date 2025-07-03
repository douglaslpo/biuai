import asyncio
import logging
import os
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8001"))
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
MEM0_PROFILE = os.getenv("MEM0_PROFILE")
MEM0_SERVER_URL = os.getenv("MEM0_SERVER_URL")

if not all([MEM0_API_KEY, MEM0_PROFILE, MEM0_SERVER_URL]):
    raise ValueError("Variáveis de ambiente MEM0 necessárias não foram definidas")

# Modelos Pydantic
class MemoryCreateRequest(BaseModel):
    content: str
    user_id: str
    metadata: Optional[Dict[str, Any]] = None

class MemorySearchRequest(BaseModel):
    query: str
    user_id: str
    limit: Optional[int] = 10

class MemoryUpdateRequest(BaseModel):
    memory_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class MemoryResponse(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str

class SearchResult(BaseModel):
    memories: List[MemoryResponse]
    total: int

# Cliente MCP
class MCPMemoryClient:
    def __init__(self):
        self.base_url = MEM0_SERVER_URL
        self.api_key = MEM0_API_KEY
        self.profile = MEM0_PROFILE
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def create_memory(self, content: str, user_id: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Criar uma nova memória"""
        async with httpx.AsyncClient() as client:
            payload = {
                "content": content,
                "user_id": user_id,
                "profile": self.profile
            }
            if metadata:
                payload["metadata"] = metadata
            
            try:
                response = await client.post(
                    f"{self.base_url}/memories",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Erro ao criar memória: {e}")
                raise HTTPException(status_code=500, detail=f"Erro ao conectar com o servidor MCP: {str(e)}")

    async def search_memories(self, query: str, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Buscar memórias"""
        async with httpx.AsyncClient() as client:
            params = {
                "query": query,
                "user_id": user_id,
                "profile": self.profile,
                "limit": limit
            }
            
            try:
                response = await client.get(
                    f"{self.base_url}/memories/search",
                    params=params,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Erro ao buscar memórias: {e}")
                raise HTTPException(status_code=500, detail=f"Erro ao conectar com o servidor MCP: {str(e)}")

    async def get_memories(self, user_id: str, limit: int = 100) -> Dict[str, Any]:
        """Obter todas as memórias do usuário"""
        async with httpx.AsyncClient() as client:
            params = {
                "user_id": user_id,
                "profile": self.profile,
                "limit": limit
            }
            
            try:
                response = await client.get(
                    f"{self.base_url}/memories",
                    params=params,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Erro ao obter memórias: {e}")
                raise HTTPException(status_code=500, detail=f"Erro ao conectar com o servidor MCP: {str(e)}")

    async def update_memory(self, memory_id: str, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Atualizar uma memória"""
        async with httpx.AsyncClient() as client:
            payload = {
                "content": content,
                "profile": self.profile
            }
            if metadata:
                payload["metadata"] = metadata
            
            try:
                response = await client.put(
                    f"{self.base_url}/memories/{memory_id}",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Erro ao atualizar memória: {e}")
                raise HTTPException(status_code=500, detail=f"Erro ao conectar com o servidor MCP: {str(e)}")

    async def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Deletar uma memória"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.base_url}/memories/{memory_id}",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return {"message": "Memória deletada com sucesso"}
            except httpx.HTTPError as e:
                logger.error(f"Erro ao deletar memória: {e}")
                raise HTTPException(status_code=500, detail=f"Erro ao conectar com o servidor MCP: {str(e)}")

# Instância global do cliente
mcp_client = MCPMemoryClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    logger.info("Iniciando serviço MCP Memory...")
    logger.info(f"Servidor configurado para: {MEM0_SERVER_URL}")
    logger.info(f"Perfil: {MEM0_PROFILE}")
    yield
    logger.info("Parando serviço MCP Memory...")

# Aplicação FastAPI
app = FastAPI(
    title="BIUAI MCP Memory Service",
    description="Serviço de integração com MCP Memory Server (Mem0 AI)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints
@app.get("/health")
async def health_check():
    """Health check do serviço"""
    return {"status": "healthy", "service": "MCP Memory Service"}

@app.post("/memories", response_model=MemoryResponse)
async def create_memory(request: MemoryCreateRequest):
    """Criar uma nova memória"""
    try:
        result = await mcp_client.create_memory(
            content=request.content,
            user_id=request.user_id,
            metadata=request.metadata
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao criar memória: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/memories/search", response_model=SearchResult)
async def search_memories(query: str, user_id: str, limit: int = 10):
    """Buscar memórias por consulta"""
    try:
        result = await mcp_client.search_memories(
            query=query,
            user_id=user_id,
            limit=limit
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar memórias: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/memories/{user_id}", response_model=SearchResult)
async def get_user_memories(user_id: str, limit: int = 100):
    """Obter todas as memórias de um usuário"""
    try:
        result = await mcp_client.get_memories(
            user_id=user_id,
            limit=limit
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao obter memórias: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.put("/memories/{memory_id}", response_model=MemoryResponse)
async def update_memory(memory_id: str, request: MemoryUpdateRequest):
    """Atualizar uma memória existente"""
    try:
        result = await mcp_client.update_memory(
            memory_id=memory_id,
            content=request.content,
            metadata=request.metadata
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar memória: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str):
    """Deletar uma memória"""
    try:
        result = await mcp_client.delete_memory(memory_id=memory_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao deletar memória: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "BIUAI MCP Memory Service",
        "version": "1.0.0",
        "server_url": MEM0_SERVER_URL,
        "profile": MEM0_PROFILE
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=MCP_SERVER_HOST,
        port=MCP_SERVER_PORT,
        reload=True,
        log_level="info"
    ) 