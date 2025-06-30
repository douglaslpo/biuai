"""
BIUAI - Sistema Financeiro Inteligente
API Principal construída com FastAPI seguindo as melhores práticas de 2024

Funcionalidades:
- Autenticação JWT avançada
- Rate limiting e segurança
- Monitoramento e métricas
- Logging estruturado
- Documentação automática
- Cache inteligente
- Validação robusta
"""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.database import init_db, close_db
from app.middleware import setup_middleware, setup_exception_handlers
from app.api.v1.api import api_router
from app.core.security import SecurityAudit


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Iniciando BIUAI API...")
    
    # Initialize database
    await init_db()
    print("✅ Banco de dados inicializado")
    
    # Log startup
    SecurityAudit.log_security_event(
        "application_startup",
        details={
            "environment": settings.ENVIRONMENT,
            "version": settings.PROJECT_VERSION,
            "debug": settings.DEBUG
        }
    )
    
    yield
    
    # Shutdown
    print("🛑 Finalizando BIUAI API...")
    
    # Close database connections
    await close_db()
    print("✅ Conexões de banco fechadas")
    
    # Log shutdown
    SecurityAudit.log_security_event(
        "application_shutdown",
        details={"environment": settings.ENVIRONMENT}
    )


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="""
    ## BIUAI - Sistema Financeiro Inteligente 🏦
    
    API completa para gestão financeira pessoal e empresarial com inteligência artificial.
    
    ### Funcionalidades Principais:
    * 🔐 **Autenticação JWT** - Sistema seguro de login e registro
    * 💰 **Gestão de Lançamentos** - Controle completo de receitas e despesas  
    * 📊 **Categorias Inteligentes** - Classificação automática com ML
    * 🎯 **Metas Financeiras** - Definição e acompanhamento de objetivos
    * 📈 **Dashboards** - Visualizações e relatórios interativos
    * 🤖 **IA Financeira** - Insights e recomendações personalizadas
    * 📱 **API RESTful** - Integração com aplicações móveis e web
    
    ### Tecnologias:
    * **FastAPI** - Framework web moderno e performático
    * **PostgreSQL** - Banco de dados robusto e escalável
    * **Redis** - Cache e sessões em tempo real
    * **JWT** - Autenticação segura e stateless
    * **SQLAlchemy** - ORM avançado com async/await
    * **Machine Learning** - Classificação e predições automáticas
    
    ### Segurança:
    * Rate limiting por IP
    * Headers de segurança obrigatórios
    * Validação rigorosa de dados
    * Auditoria de ações
    * Criptografia de senhas com bcrypt
    * Tokens JWT com expiração configurável
    
    ---
    **Desenvolvido por:** Equipe BIUAI  
    **Ambiente:** {environment}  
    **Versão:** {version}
    """.format(
        environment=settings.ENVIRONMENT,
        version=settings.PROJECT_VERSION
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=None,  # Disabled, we'll use custom
    redoc_url=None,  # Disabled, we'll use custom
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    lifespan=lifespan,
    contact={
        "name": "BIUAI Support",
        "email": "suporte@biuai.com",
        "url": "https://biuai.com/suporte"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://biuai.com/licenca"
    },
    terms_of_service="https://biuai.com/termos"
)

# Setup middleware
setup_middleware(app)

# Setup exception handlers
setup_exception_handlers(app)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


# Health Check Endpoint
@app.get("/", response_model=Dict[str, Any], tags=["System"])
async def root() -> Dict[str, Any]:
    """
    Endpoint raiz da API - Informações do sistema
    """
    return {
        "message": "🏦 BIUAI - Sistema Financeiro Inteligente",
        "version": settings.PROJECT_VERSION,
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "documentation": "/docs",
        "api_version": "v1",
        "features": [
            "Autenticação JWT",
            "Gestão Financeira",
            "Machine Learning",
            "API RESTful",
            "Monitoramento",
            "Cache Inteligente"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc", 
            "openapi": f"{settings.API_V1_STR}/openapi.json",
            "health": "/health",
            "metrics": "/metrics"
        }
    }


# Custom Documentation Pages
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with enhanced styling"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Documentação",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui.css",
        swagger_favicon_url="/static/favicon.ico",
        swagger_ui_parameters={
            "deepLinking": True,
            "displayRequestDuration": True,
            "docExpansion": "list",
            "operationsSorter": "alpha",
            "filter": True,
            "tagsSorter": "alpha",
            "tryItOutEnabled": True,
            "displayOperationId": False,
            "showExtensions": True,
            "showCommonExtensions": True,
            "persistAuthorization": True,
            "layout": "BaseLayout"
        }
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Custom ReDoc documentation"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Documentação",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.1.3/bundles/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.ico",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    """OAuth2 redirect for Swagger UI"""
    return get_swagger_ui_oauth2_redirect_html()


def custom_openapi():
    """Custom OpenAPI schema with enhanced metadata"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        contact=app.contact,
        license_info=app.license_info,
        terms_of_service=app.terms_of_service
    )
    
    # Force OpenAPI 3.0.0 for Swagger UI compatibility
    openapi_schema["openapi"] = "3.0.0"
    
    # Enhanced security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT obtido através do endpoint de login"
        },
        "APIKey": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Chave de API para integrações"
        }
    }
    
    # Add custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "/static/images/biuai-logo.svg",
        "altText": "BIUAI Logo"
    }
    
    # Add servers information
    openapi_schema["servers"] = [
        {
            "url": f"http://localhost:3000",
            "description": "Servidor de Desenvolvimento"
        },
        {
            "url": f"https://api.biuai.com",
            "description": "Servidor de Produção"
        }
    ]
    
    # Add tags metadata
    openapi_schema["tags"] = [
        {
            "name": "System",
            "description": "Endpoints do sistema - saúde, métricas e informações"
        },
        {
            "name": "Authentication", 
            "description": "Autenticação e autorização de usuários"
        },
        {
            "name": "Users",
            "description": "Gerenciamento de usuários e perfis"
        },
        {
            "name": "Lancamentos",
            "description": "Gestão de lançamentos financeiros (receitas e despesas)"
        },
        {
            "name": "Categorias",
            "description": "Categorias de lançamentos financeiros"
        },
        {
            "name": "Metas",
            "description": "Metas e objetivos financeiros"
        },
        {
            "name": "Analytics",
            "description": "Relatórios e análises financeiras"
        },
        {
            "name": "ML",
            "description": "Endpoints de machine learning e IA"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Set custom OpenAPI
app.openapi = custom_openapi


# Static files (if needed)
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Enhanced startup message
@app.on_event("startup")
async def startup_message():
    """Display enhanced startup information"""
    print("\n" + "="*60)
    print("🏦 BIUAI - Sistema Financeiro Inteligente")
    print("="*60)
    print(f"📊 Versão: {settings.PROJECT_VERSION}")
    print(f"🌍 Ambiente: {settings.ENVIRONMENT}")
    print(f"🔧 Debug: {settings.DEBUG}")
    print(f"🚀 Servidor: http://localhost:3000")
    print(f"📚 Documentação: http://localhost:3000/docs")
    print(f"⚡ API: http://localhost:3000{settings.API_V1_STR}")
    print(f"🔍 Métricas: http://localhost:3000/metrics")
    print(f"💓 Health: http://localhost:3000/health")
    print("="*60)
    
    if settings.ENVIRONMENT == "development":
        print("⚠️  MODO DESENVOLVIMENTO - NÃO USE EM PRODUÇÃO!")
        print("="*60)
    
    print("✅ Sistema pronto para uso!")
    print("\n")


# Custom error pages
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    """Custom 404 error page"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint não encontrado",
            "message": "A rota solicitada não existe nesta API",
            "suggestion": "Verifique a documentação em /docs",
            "available_endpoints": [
                "/docs - Documentação",
                "/health - Status do sistema", 
                "/metrics - Métricas de performance",
                f"{settings.API_V1_STR}/auth/login - Login",
                f"{settings.API_V1_STR}/auth/register - Registro"
            ]
        }
    )


@app.exception_handler(405)
async def custom_405_handler(request: Request, exc):
    """Custom 405 method not allowed"""
    return JSONResponse(
        status_code=405,
        content={
            "detail": "Método não permitido",
            "message": f"O método {request.method} não é permitido para {request.url.path}",
            "suggestion": "Verifique a documentação para os métodos HTTP aceitos"
        }
    )


# Graceful shutdown handler
@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown procedures"""
    print("\n🛑 Iniciando shutdown graceful...")
    
    # Wait a bit for ongoing requests
    await asyncio.sleep(1)
    
    print("✅ Shutdown concluído com sucesso!")


if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
        access_log=settings.DEBUG,
        use_colors=True,
        server_header=False,
        date_header=False
    ) 