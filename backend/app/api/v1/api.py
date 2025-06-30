from fastapi import APIRouter

from app.api.v1.endpoints import auth, lancamentos, users
from app.routes import financeiro, memoria, chatbot

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(lancamentos.router, prefix="/lancamentos", tags=["lancamentos"])
api_router.include_router(financeiro.router, prefix="/financeiro", tags=["financeiro"])
api_router.include_router(memoria.router, prefix="/memoria", tags=["memoria"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"]) 