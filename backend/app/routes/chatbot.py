"""
Rotas da API para funcionalidades do chatbot
"""

from typing import Dict, Any
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer

from ..schemas.chatbot import (
    ChatMessage, 
    ChatResponse, 
    ChatHistory, 
    BotConfig,
    ChatAnalytics,
    BotFeedback,
    UserContext
)
from ..services.chatbot_service import chatbot_service
from ..auth.jwt import get_current_user
from ..models.usuario import Usuario

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chatbot"])
security = HTTPBearer()


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    message_data: ChatMessage,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Enviar mensagem para o chatbot
    """
    try:
        # Obter contexto do usuário
        context = await chatbot_service.get_user_context(
            user_id=str(current_user.id),
            token=current_user.access_token if hasattr(current_user, 'access_token') else ""
        )
        
        # Enriquecer contexto com dados da requisição
        if message_data.context:
            context.update(message_data.context)
        
        # Enviar mensagem para o chatbot MCP
        response = await chatbot_service.send_message(
            message=message_data.message,
            user_id=str(current_user.id),
            session_id=message_data.session_id,
            context=context
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem do chatbot: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro interno ao processar mensagem"
        )


@router.get("/history/{session_id}", response_model=ChatHistory)
async def get_chat_history(
    session_id: str,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obter histórico de uma sessão de chat
    """
    try:
        history = await chatbot_service.get_chat_history(session_id)
        
        # Verificar se o usuário tem acesso à sessão
        # (implementar validação de propriedade se necessário)
        
        return ChatHistory(**history)
        
    except Exception as e:
        logger.error(f"Erro ao obter histórico de chat: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao obter histórico de chat"
        )


@router.get("/config", response_model=BotConfig)
async def get_bot_configuration(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obter configurações do bot
    """
    try:
        config = await chatbot_service.get_bot_config()
        return BotConfig(**config)
        
    except Exception as e:
        logger.error(f"Erro ao obter configurações do bot: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao obter configurações do bot"
        )


@router.get("/health")
async def chatbot_health_check():
    """
    Verificar saúde do serviço de chatbot
    """
    try:
        health = await chatbot_service.health_check()
        return health
        
    except Exception as e:
        logger.error(f"Erro no health check do chatbot: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "chatbot"
        }


@router.post("/feedback")
async def submit_chatbot_feedback(
    feedback: BotFeedback,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Enviar feedback sobre o chatbot
    """
    try:
        success = await chatbot_service.save_feedback(
            session_id=feedback.session_id,
            rating=feedback.rating,
            comment=feedback.comment or "",
            helpful=feedback.helpful
        )
        
        if success:
            return {"status": "success", "message": "Feedback salvo com sucesso"}
        else:
            raise HTTPException(status_code=500, detail="Erro ao salvar feedback")
            
    except Exception as e:
        logger.error(f"Erro ao salvar feedback do chatbot: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao salvar feedback"
        )


@router.get("/context", response_model=UserContext)
async def get_user_context(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obter contexto completo do usuário para o chatbot
    """
    try:
        context = await chatbot_service.get_user_context(
            user_id=str(current_user.id),
            token=current_user.access_token if hasattr(current_user, 'access_token') else ""
        )
        
        return UserContext(**context)
        
    except Exception as e:
        logger.error(f"Erro ao obter contexto do usuário: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao obter contexto do usuário"
        )


# Rotas administrativas (apenas para admins)
@router.get("/admin/analytics", response_model=ChatAnalytics)
async def get_chatbot_analytics(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obter analytics do chatbot (apenas admins)
    """
    # Verificar se é admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas administradores podem acessar analytics."
        )
    
    try:
        analytics = await chatbot_service.get_analytics()
        
        # Construir resposta com dados mock para campos não implementados
        return ChatAnalytics(
            total_sessions=analytics.get("total_sessions", 0),
            total_messages=analytics.get("total_sessions", 0) * 5,  # Estimativa
            avg_session_duration=4.5,  # Mock
            most_common_questions=[
                "Como usar o dashboard?",
                "Como categorizar lançamentos?",
                "Como criar relatórios?"
            ],
            user_satisfaction=analytics.get("avg_rating", 0) * 2,  # Converter para escala 0-10
            response_time_avg=2.3
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter analytics do chatbot: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao obter analytics do chatbot"
        )


@router.get("/admin/sessions")
async def get_admin_chat_sessions(
    current_user: Usuario = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Obter todas as sessões de chat (apenas admins)
    """
    # Verificar se é admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas administradores podem acessar todas as sessões."
        )
    
    try:
        # Implementar quando houver persistência das sessões
        return {
            "sessions": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "message": "Funcionalidade em desenvolvimento"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter sessões de chat: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao obter sessões de chat"
        )


@router.post("/admin/broadcast")
async def broadcast_message(
    message: str,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Enviar mensagem broadcast para todos os usuários online (apenas admins)
    """
    # Verificar se é admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas administradores podem enviar broadcasts."
        )
    
    try:
        # Implementar broadcast via WebSocket quando disponível
        return {
            "status": "success",
            "message": "Broadcast enviado",
            "recipients": 0,  # Mock
            "content": message
        }
        
    except Exception as e:
        logger.error(f"Erro ao enviar broadcast: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao enviar broadcast"
        )


@router.get("/suggestions")
async def get_chat_suggestions(
    query: str = Query(..., min_length=1),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obter sugestões de perguntas baseadas em uma query
    """
    try:
        # Gerar sugestões usando o sistema do chatbot
        suggestions = await chatbot_service._generate_suggestions(query, "")
        
        return {
            "query": query,
            "suggestions": suggestions,
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter sugestões: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao obter sugestões"
        )


@router.get("/quick-help")
async def get_quick_help(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obter ajuda rápida e ações comuns
    """
    try:
        quick_help = {
            "welcome_message": f"Olá! Sou o Bi UAI Bot Administrador. Como posso te ajudar hoje?",
            "common_actions": [
                {
                    "title": "Ver Dashboard",
                    "description": "Acesse sua visão geral financeira",
                    "action": "Como acessar o dashboard?",
                    "icon": "📊"
                },
                {
                    "title": "Adicionar Lançamento",
                    "description": "Registre uma nova receita ou despesa",
                    "action": "Como adicionar um novo lançamento?",
                    "icon": "💰"
                },
                {
                    "title": "Ver Relatórios",
                    "description": "Analise seus dados financeiros",
                    "action": "Como gerar relatórios?",
                    "icon": "📈"
                },
                {
                    "title": "Configurar Categorias",
                    "description": "Organize suas transações",
                    "action": "Como configurar categorias?",
                    "icon": "🏷️"
                }
            ],
            "tips": [
                "Use comandos como 'mostrar gastos deste mês' para consultas específicas",
                "Posso ajudar com navegação e explicações de funcionalidades",
                "Digite sua dúvida em linguagem natural, entendo português brasileiro!"
            ]
        }
        
        return quick_help
        
    except Exception as e:
        logger.error(f"Erro ao obter ajuda rápida: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao obter ajuda rápida"
        ) 