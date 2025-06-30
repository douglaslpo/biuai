"""
Schemas para funcionalidades do chatbot
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Schema para mensagem de chat"""
    message: str = Field(..., description="Mensagem do usuário")
    session_id: Optional[str] = Field(None, description="ID da sessão de chat")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Como posso ver meus gastos deste mês?",
                "session_id": "session_123",
                "context": {
                    "current_page": "/dashboard",
                    "user_id": "user123"
                }
            }
        }


class ChatResponse(BaseModel):
    """Schema de resposta do chatbot"""
    response: str = Field(..., description="Resposta do bot")
    session_id: str = Field(..., description="ID da sessão")
    timestamp: str = Field(..., description="Timestamp da resposta")
    bot_name: str = Field(..., description="Nome do bot")
    suggestions: Optional[List[str]] = Field(None, description="Sugestões de próximas perguntas")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "Para ver seus gastos deste mês, acesse o Dashboard e veja o gráfico de despesas...",
                "session_id": "session_123",
                "timestamp": "2024-01-15T10:30:00Z",
                "bot_name": "Bi UAI Bot Administrador",
                "suggestions": [
                    "Como categorizar meus gastos?",
                    "Quais são minhas maiores despesas?",
                    "Como definir uma meta de economia?"
                ]
            }
        }


class ChatHistory(BaseModel):
    """Schema para histórico de chat"""
    session_id: str = Field(..., description="ID da sessão")
    messages: List[Dict[str, Any]] = Field(..., description="Lista de mensagens")
    created_at: str = Field(..., description="Data de criação da sessão")
    updated_at: str = Field(..., description="Data da última atualização")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_123",
                "messages": [
                    {
                        "message": "Olá, como posso ajudar?",
                        "timestamp": "2024-01-15T10:25:00Z",
                        "is_bot": True
                    },
                    {
                        "message": "Como vejo meus gastos?",
                        "timestamp": "2024-01-15T10:26:00Z",
                        "is_bot": False
                    }
                ],
                "created_at": "2024-01-15T10:25:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class BotConfig(BaseModel):
    """Schema para configurações do bot"""
    bot_name: str = Field(..., description="Nome do bot")
    personality: str = Field(..., description="Personalidade do bot")
    system_prompt: str = Field(..., description="Prompt do sistema")
    model_name: str = Field(..., description="Nome do modelo de IA")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperatura para geração")
    max_tokens: int = Field(1000, ge=100, le=4000, description="Máximo de tokens")
    enabled: bool = Field(True, description="Bot habilitado")
    knowledge_base_version: str = Field("1.0", description="Versão da base de conhecimento")
    
    class Config:
        schema_extra = {
            "example": {
                "bot_name": "Bi UAI Bot Administrador",
                "personality": "amigável e profissional",
                "system_prompt": "Você é um assistente especialista em finanças...",
                "model_name": "llama3.2:3b",
                "temperature": 0.7,
                "max_tokens": 1000,
                "enabled": True,
                "knowledge_base_version": "1.0"
            }
        }


class BotConfigUpdate(BaseModel):
    """Schema para atualização de configurações do bot"""
    personality: Optional[str] = Field(None, description="Nova personalidade")
    system_prompt: Optional[str] = Field(None, description="Novo prompt do sistema")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Nova temperatura")
    max_tokens: Optional[int] = Field(None, ge=100, le=4000, description="Novo máximo de tokens")
    enabled: Optional[bool] = Field(None, description="Status do bot")
    
    class Config:
        schema_extra = {
            "example": {
                "personality": "mais técnico e detalhado",
                "temperature": 0.5,
                "enabled": True
            }
        }


class ChatAnalytics(BaseModel):
    """Schema para analytics do chatbot"""
    total_sessions: int = Field(..., description="Total de sessões")
    total_messages: int = Field(..., description="Total de mensagens")
    avg_session_duration: float = Field(..., description="Duração média da sessão (minutos)")
    most_common_questions: List[str] = Field(..., description="Perguntas mais comuns")
    user_satisfaction: float = Field(..., description="Satisfação do usuário (0-10)")
    response_time_avg: float = Field(..., description="Tempo médio de resposta (segundos)")
    
    class Config:
        schema_extra = {
            "example": {
                "total_sessions": 150,
                "total_messages": 850,
                "avg_session_duration": 5.2,
                "most_common_questions": [
                    "Como ver meus gastos?",
                    "Como categorizar transações?",
                    "Como definir metas?"
                ],
                "user_satisfaction": 8.5,
                "response_time_avg": 2.3
            }
        }


class UserContext(BaseModel):
    """Schema para contexto do usuário"""
    user_id: str = Field(..., description="ID do usuário")
    current_page: Optional[str] = Field(None, description="Página atual")
    recent_actions: Optional[List[str]] = Field(None, description="Ações recentes")
    financial_summary: Optional[Dict[str, Any]] = Field(None, description="Resumo financeiro")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Preferências do usuário")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "current_page": "/dashboard",
                "recent_actions": ["visualizou dashboard", "criou lançamento"],
                "financial_summary": {
                    "total_receitas": 5000.0,
                    "total_despesas": 3500.0,
                    "saldo": 1500.0
                },
                "preferences": {
                    "tema": "escuro",
                    "notificacoes": True
                }
            }
        }


class BotKnowledgeItem(BaseModel):
    """Schema para item da base de conhecimento"""
    id: Optional[str] = Field(None, description="ID do item")
    category: str = Field(..., description="Categoria do conhecimento")
    title: str = Field(..., description="Título do item")
    content: str = Field(..., description="Conteúdo do item")
    keywords: List[str] = Field(..., description="Palavras-chave")
    priority: int = Field(1, ge=1, le=10, description="Prioridade (1-10)")
    active: bool = Field(True, description="Item ativo")
    
    class Config:
        schema_extra = {
            "example": {
                "category": "funcionalidades",
                "title": "Dashboard",
                "content": "O Dashboard oferece uma visão completa das finanças...",
                "keywords": ["dashboard", "visão geral", "gráficos"],
                "priority": 5,
                "active": True
            }
        }


class BotFeedback(BaseModel):
    """Schema para feedback do usuário sobre o bot"""
    session_id: str = Field(..., description="ID da sessão")
    rating: int = Field(..., ge=1, le=5, description="Avaliação (1-5)")
    comment: Optional[str] = Field(None, description="Comentário opcional")
    helpful: bool = Field(..., description="Resposta foi útil")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_123",
                "rating": 5,
                "comment": "Bot muito útil e rápido!",
                "helpful": True
            }
        } 