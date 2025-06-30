"""
Serviço para integração com MCP Chatbot Service
"""

import logging
from typing import Dict, Any, List, Optional
import httpx
import json
from datetime import datetime
from fastapi import HTTPException

from ..core.config import settings
from ..services.cache import cache

logger = logging.getLogger(__name__)


class ChatbotService:
    """Serviço para interação com o chatbot MCP"""
    
    def __init__(self):
        self.base_url = settings.MCP_CHATBOT_SERVICE_URL
        self.timeout = float(settings.MCP_CHATBOT_SERVICE_TIMEOUT)
        self.cache = cache
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Fazer requisição HTTP para o serviço MCP Chatbot"""
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
                    raise HTTPException(status_code=500, detail="Erro interno do serviço de chatbot")
            except httpx.RequestError as e:
                logger.error(f"Erro de conexão com o serviço MCP Chatbot: {e}")
                raise HTTPException(status_code=503, detail="Serviço de chatbot indisponível")
    
    async def send_message(
        self, 
        message: str, 
        user_id: str, 
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Enviar mensagem para o chatbot"""
        payload = {
            "message": message,
            "user_id": user_id,
            "session_id": session_id,
            "context": context or {}
        }
        
        try:
            response = await self._make_request("POST", "/chat", json=payload)
            
            # Enriquecer resposta com sugestões
            if response.get("response"):
                suggestions = await self._generate_suggestions(message, response["response"])
                response["suggestions"] = suggestions
            
            return response
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para chatbot: {e}")
            # Fallback para resposta padrão
            return {
                "response": "Desculpe, estou temporariamente indisponível. Tente novamente em alguns instantes.",
                "session_id": session_id or f"fallback_{user_id}_{datetime.now().timestamp()}",
                "timestamp": datetime.now().isoformat(),
                "bot_name": settings.BOT_NAME,
                "suggestions": ["Como posso te ajudar?", "Qual é a dúvida?"]
            }
    
    async def get_chat_history(self, session_id: str) -> Dict[str, Any]:
        """Obter histórico de chat"""
        try:
            return await self._make_request("GET", f"/chat/history/{session_id}")
        except HTTPException as e:
            if e.status_code == 404:
                return {"session_id": session_id, "messages": []}
            raise
    
    async def get_bot_config(self) -> Dict[str, Any]:
        """Obter configurações do bot"""
        return await self._make_request("GET", "/config")
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar saúde do serviço chatbot"""
        try:
            return await self._make_request("GET", "/health")
        except Exception as e:
            logger.error(f"Health check do chatbot falhou: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def _generate_suggestions(self, user_message: str, bot_response: str) -> List[str]:
        """Gerar sugestões baseadas na conversa"""
        # Cache de sugestões por contexto
        cache_key = f"suggestions:{hash(user_message[:50])}"
        cached = self.cache.get(cache_key) if self.cache else None
        
        if cached:
            return json.loads(cached)
        
        # Sugestões baseadas em palavras-chave
        suggestions_map = {
            "dashboard": [
                "Como interpretar os gráficos do dashboard?",
                "Quais métricas são mais importantes?",
                "Como personalizar o dashboard?"
            ],
            "lançamento": [
                "Como categorizar automaticamente?",
                "Como editar um lançamento?",
                "Como importar dados de banco?"
            ],
            "categoria": [
                "Como criar uma nova categoria?",
                "Como alterar categoria de vários lançamentos?",
                "Quais são as categorias padrão?"
            ],
            "meta": [
                "Como definir uma meta realista?",
                "Como acompanhar progresso da meta?",
                "Como editar uma meta existente?"
            ],
            "relatório": [
                "Como gerar relatório personalizado?",
                "Como exportar dados?",
                "Como comparar períodos?"
            ],
            "ajuda": [
                "Como navegar no sistema?",
                "Onde encontro tutoriais?",
                "Como entrar em contato com suporte?"
            ]
        }
        
        # Detectar contexto e gerar sugestões
        user_lower = user_message.lower()
        suggestions = []
        
        for keyword, suggestion_list in suggestions_map.items():
            if keyword in user_lower:
                suggestions.extend(suggestion_list[:2])  # Máximo 2 por categoria
        
        # Sugestões padrão se nenhuma específica foi encontrada
        if not suggestions:
            suggestions = [
                "Como posso melhorar minha organização financeira?",
                "Quais relatórios você recomenda?",
                "Como usar a IA para insights?"
            ]
        
        # Limitar a 3 sugestões
        final_suggestions = suggestions[:3]
        
        # Cache por 1 hora
        if self.cache:
            self.cache.set(cache_key, json.dumps(final_suggestions), ttl=3600)
        
        return final_suggestions
    
    async def get_user_context(self, user_id: str, token: str) -> Dict[str, Any]:
        """Obter contexto completo do usuário para o chatbot"""
        context = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Buscar dados financeiros
            async with httpx.AsyncClient() as client:
                # Resumo financeiro
                response = await client.get(
                    f"{settings.API_V1_STR}/financeiro/resumo",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    context["financial_summary"] = response.json()
                
                # Dados do usuário
                response = await client.get(
                    f"{settings.API_V1_STR}/users/me",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    user_data = response.json()
                    context["user_data"] = {
                        "name": user_data.get("nome"),
                        "email": user_data.get("email"),
                        "created_at": user_data.get("created_at")
                    }
        
        except Exception as e:
            logger.warning(f"Erro ao obter contexto do usuário {user_id}: {e}")
        
        return context
    
    async def save_feedback(self, session_id: str, rating: int, comment: str, helpful: bool) -> bool:
        """Salvar feedback do usuário sobre o chatbot"""
        try:
            if self.cache:
                feedback_data = {
                    "session_id": session_id,
                    "rating": rating,
                    "comment": comment,
                    "helpful": helpful,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Salvar feedback individual
                self.cache.set(
                    f"feedback:{session_id}", 
                    json.dumps(feedback_data), 
                    ttl=2592000  # 30 dias
                )
                
                # Atualizar estatísticas agregadas
                await self._update_feedback_stats(rating, helpful)
                
                return True
        except Exception as e:
            logger.error(f"Erro ao salvar feedback: {e}")
            return False
    
    async def _update_feedback_stats(self, rating: int, helpful: bool):
        """Atualizar estatísticas de feedback"""
        try:
            if not self.cache:
                return
            
            stats_key = "chatbot:feedback_stats"
            stats = self.cache.get(stats_key)
            
            if stats:
                stats = json.loads(stats)
            else:
                stats = {
                    "total_feedback": 0,
                    "total_rating": 0,
                    "helpful_count": 0
                }
            
            stats["total_feedback"] += 1
            stats["total_rating"] += rating
            stats["helpful_count"] += 1 if helpful else 0
            
            self.cache.set(stats_key, json.dumps(stats), ttl=2592000)  # 30 dias
            
        except Exception as e:
            logger.error(f"Erro ao atualizar estatísticas de feedback: {e}")
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Obter analytics do chatbot"""
        try:
            if not self.cache:
                return {"error": "Cache não disponível"}
            
            # Buscar estatísticas de feedback
            stats_key = "chatbot:feedback_stats"
            feedback_stats = self.cache.get(stats_key)
            
            if feedback_stats:
                stats = json.loads(feedback_stats)
                avg_rating = stats["total_rating"] / stats["total_feedback"] if stats["total_feedback"] > 0 else 0
                helpful_percentage = (stats["helpful_count"] / stats["total_feedback"] * 100) if stats["total_feedback"] > 0 else 0
            else:
                avg_rating = 0
                helpful_percentage = 0
                stats = {"total_feedback": 0}
            
            return {
                "total_sessions": stats.get("total_feedback", 0),  # Aproximação
                "avg_rating": round(avg_rating, 2),
                "helpful_percentage": round(helpful_percentage, 2),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter analytics: {e}")
            return {"error": str(e)}


# Instância global do serviço
chatbot_service = ChatbotService() 