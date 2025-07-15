from typing import Optional
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from sqlalchemy import select

from app.core.config import settings
from app.models.tenant import Tenant
from app.database import get_db

class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware para gerenciar contexto do tenant"""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Processa a requisição"""
        
        # Ignorar rotas públicas
        if self._is_public_route(request.url.path):
            return await call_next(request)
        
        # Obter tenant do header ou domínio
        tenant = await self._get_tenant(request)
        if not tenant:
            raise HTTPException(
                status_code=404,
                detail="Tenant não encontrado"
            )
        
        # Verificar se tenant está ativo
        if not tenant.is_active:
            raise HTTPException(
                status_code=403,
                detail="Tenant inativo"
            )
        
        # Verificar se tem acesso ao sistema
        if not tenant.has_active_subscription:
            raise HTTPException(
                status_code=402,
                detail="Assinatura expirada"
            )
        
        # Adicionar tenant ao request state
        request.state.tenant = tenant
        request.state.tenant_id = tenant.id
        
        try:
            response = await call_next(request)
            return response
        finally:
            pass
    
    def _is_public_route(self, path: str) -> bool:
        """Verifica se é uma rota pública"""
        public_routes = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
            "/api/v1/tenants/register"
        ]
        return any(path.startswith(route) for route in public_routes)
    
    async def _get_tenant(self, request: Request) -> Optional[Tenant]:
        """Obtém o tenant da requisição"""
        db_gen = get_db()
        db = await anext(db_gen)
        
        # Tentar obter do header
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id and tenant_id.isdigit():
            result = await db.execute(select(Tenant).filter(Tenant.id == int(tenant_id)))
            return result.scalars().first()
        
        # Tentar obter do subdomínio
        host = request.headers.get("host", "").split(":")[0]
        if "." in host:
            subdomain = host.split(".")[0]
            if subdomain != "www":
                result = await db.execute(select(Tenant).filter(Tenant.slug == subdomain))
                return result.scalars().first()
        
        # Tentar obter do domínio completo
        result = await db.execute(select(Tenant).filter(Tenant.domain == host))
        return result.scalars().first() 