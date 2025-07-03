from fastapi import APIRouter

from app.api.v1.endpoints import auth, lancamentos, users
from app.routes import financeiro, memoria, chatbot, metas, contas, data_import

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(lancamentos.router, prefix="/lancamentos", tags=["lancamentos"])
api_router.include_router(financeiro.router, prefix="/financeiro", tags=["financeiro"])
api_router.include_router(metas.router, prefix="/metas", tags=["metas"])
api_router.include_router(contas.router, prefix="/contas", tags=["contas"])
api_router.include_router(memoria.router, prefix="/memoria", tags=["memoria"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
api_router.include_router(data_import.router, prefix="/data-import", tags=["data-import"]) 