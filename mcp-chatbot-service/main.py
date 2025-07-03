"""
BIUAI MCP Chatbot Service - Bi UAI Bot Administrador
Chatbot especialista em IA gratuita usando Ollama
"""

import asyncio
import logging
import os
import json
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import ollama
import redis.asyncio as redis
from dotenv import load_dotenv
import structlog

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Configurações
MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8002"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:3000")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/1")
BOT_NAME = os.getenv("BOT_NAME", "Bi UAI Bot Administrador")

# Modelos Pydantic
class ChatMessage(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    bot_name: str = BOT_NAME

class BotConfig(BaseModel):
    personality: str
    system_prompt: str
    model_name: str = "llama3.2:1b"  # Modelo menor para usar menos memória
    temperature: float = 0.7
    max_tokens: int = 1000
    enabled: bool = True

class ChatSession(BaseModel):
    session_id: str
    user_id: str
    messages: List[Dict[str, Any]]
    created_at: str
    updated_at: str

# Cliente Ollama
class OllamaClient:
    def __init__(self):
        self.client = ollama.Client(host=OLLAMA_BASE_URL)
        self.default_model = "llama3.2:1b"
    
    async def ensure_model(self, model_name: str = None):
        """Garantir que o modelo está disponível"""
        model = model_name or self.default_model
        try:
            # Listar modelos disponíveis
            models = self.client.list()
            model_names = [m['name'] for m in models['models']]
            
            if model not in model_names:
                logger.info(f"Baixando modelo {model}...")
                self.client.pull(model)
                logger.info(f"Modelo {model} baixado com sucesso")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar/baixar modelo: {e}")
            return False
    
    async def generate_response(self, prompt: str, system_prompt: str, model: str = None) -> str:
        """Gerar resposta usando Ollama"""
        model_name = model or self.default_model
        
        try:
            response = self.client.chat(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": 0.7,
                    "num_predict": 1000,
                }
            )
            
            return response['message']['content']
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return "Desculpe, estou com dificuldades técnicas no momento. Tente novamente em instantes."

# Gerenciador de Sessões de Chat
class ChatManager:
    def __init__(self):
        self.redis_client = None
        self.connections: Dict[str, WebSocket] = {}
    
    async def connect_redis(self):
        """Conectar ao Redis"""
        self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    
    async def add_connection(self, session_id: str, websocket: WebSocket):
        """Adicionar conexão WebSocket"""
        self.connections[session_id] = websocket
    
    async def remove_connection(self, session_id: str):
        """Remover conexão WebSocket"""
        if session_id in self.connections:
            del self.connections[session_id]
    
    async def save_message(self, session_id: str, user_id: str, message: str, is_bot: bool = False):
        """Salvar mensagem no Redis"""
        if not self.redis_client:
            return
        
        message_data = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "is_bot": is_bot,
            "user_id": user_id
        }
        
        key = f"chat_session:{session_id}"
        await self.redis_client.lpush(key, json.dumps(message_data))
        await self.redis_client.expire(key, 86400)  # 24 horas
    
    async def get_session_history(self, session_id: str) -> List[Dict]:
        """Obter histórico da sessão"""
        if not self.redis_client:
            return []
        
        key = f"chat_session:{session_id}"
        messages = await self.redis_client.lrange(key, 0, -1)
        return [json.loads(msg) for msg in reversed(messages)]

# Base de Conhecimento do BIUAI
class BiuaiKnowledgeBase:
    def __init__(self):
        self.knowledge = {
            "funcionalidades": {
                "dashboard": "O Dashboard do BIUAI oferece uma visão completa das suas finanças com gráficos interativos, métricas de receitas e despesas, e insights de IA.",
                "lancamentos": "Gerencie seus lançamentos financeiros (receitas e despesas) com categorização automática e relatórios detalhados.",
                "categorias": "Sistema inteligente de categorização automática de transações usando machine learning.",
                "metas": "Defina e acompanhe metas financeiras com alertas e progresso visual.",
                "relatorios": "Relatórios avançados com análises temporais e comparações.",
                "ia": "Sistema de IA que oferece insights, recomendações e análises preditivas.",
            },
            "navegacao": {
                "dashboard": "Acesse através do menu principal ou pela URL /dashboard",
                "lancamentos": "Menu Financeiro > Lançamentos ou /lancamentos",
                "categorias": "Menu Financeiro > Categorias ou /categorias",
                "relatorios": "Menu Relatórios > Análises ou /relatorios",
                "perfil": "Clique no avatar no canto superior direito",
            },
            "ajuda": {
                "login": "Use suas credenciais de acesso. Para demo: demo@biuai.com / demo123",
                "cadastro": "Clique em 'Criar Conta' na tela de login",
                "recuperar_senha": "Use 'Esqueci minha senha' na tela de login",
                "suporte": "Entre em contato através do menu Ajuda > Suporte",
            }
        }
    
    def search_knowledge(self, query: str) -> str:
        """Buscar informações na base de conhecimento"""
        query_lower = query.lower()
        results = []
        
        for category, items in self.knowledge.items():
            for key, value in items.items():
                if query_lower in key.lower() or query_lower in value.lower():
                    results.append(f"**{key.title()}**: {value}")
        
        return "\n\n".join(results) if results else ""

# Sistema de Prompts
class PromptSystem:
    def __init__(self):
        self.system_prompt = f"""
Você é o {BOT_NAME}, um assistente especialista no sistema financeiro BIUAI.

PERSONALIDADE:
- Amigável, prestativo e profissional
- Especialista em finanças pessoais e tecnologia
- Sempre positivo e encorajador
- Fala em português brasileiro

CONHECIMENTO:
- Sistema BIUAI completo (dashboard, lançamentos, categorias, metas, relatórios)
- Finanças pessoais e investimentos
- Funcionalidades de IA e machine learning
- Navegação e usabilidade do sistema

DIRETRIZES:
- Sempre seja específico sobre funcionalidades do BIUAI
- Ofereça ajuda prática e acionável
- Use emojis moderadamente (📊 💰 ✅ 📈)
- Seja conciso mas completo
- Se não souber algo, diga que consultará com a equipe

FORMATO DE RESPOSTA:
- Use markdown quando apropriado
- Estruture respostas complexas em tópicos
- Inclua links ou referências quando necessário
- Sempre termine oferecendo mais ajuda
"""
    
    def get_context_prompt(self, user_context: Dict[str, Any]) -> str:
        """Gerar prompt com contexto do usuário"""
        context_info = []
        
        if user_context.get("current_page"):
            context_info.append(f"Usuário está na página: {user_context['current_page']}")
        
        if user_context.get("user_data"):
            context_info.append("Dados do usuário disponíveis para consulta")
        
        if user_context.get("recent_actions"):
            context_info.append(f"Ações recentes: {user_context['recent_actions']}")
        
        if context_info:
            return f"\nCONTEXTO ATUAL:\n" + "\n".join(context_info) + "\n"
        
        return ""

# Cliente para Backend BIUAI
class BiuaiBackendClient:
    def __init__(self):
        self.base_url = BACKEND_API_URL
        self.timeout = 30.0
    
    async def get_user_data(self, user_id: str, token: str) -> Dict[str, Any]:
        """Obter dados do usuário"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/me",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=self.timeout
                )
                return response.json() if response.status_code == 200 else {}
            except Exception as e:
                logger.error(f"Erro ao obter dados do usuário: {e}")
                return {}
    
    async def get_financial_summary(self, user_id: str, token: str) -> Dict[str, Any]:
        """Obter resumo financeiro"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/financeiro/resumo",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=self.timeout
                )
                return response.json() if response.status_code == 200 else {}
            except Exception as e:
                logger.error(f"Erro ao obter resumo financeiro: {e}")
                return {}

# Instâncias globais
ollama_client = OllamaClient()
chat_manager = ChatManager()
knowledge_base = BiuaiKnowledgeBase()
prompt_system = PromptSystem()
backend_client = BiuaiBackendClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    logger.info("🤖 Iniciando Bi UAI Bot Administrador...")
    
    # Conectar ao Redis
    await chat_manager.connect_redis()
    logger.info("✅ Conectado ao Redis")
    
    # Verificar/baixar modelo Ollama
    model_ready = await ollama_client.ensure_model()
    if model_ready:
        logger.info("✅ Modelo Ollama pronto")
    else:
        logger.warning("⚠️  Modelo Ollama não disponível")
    
    yield
    
    logger.info("🛑 Parando Bi UAI Bot Administrador...")

# Aplicação FastAPI
app = FastAPI(
    title="BIUAI MCP Chatbot Service",
    description="Bi UAI Bot Administrador - Assistente Inteligente Especializado",
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

# Endpoints REST
@app.get("/health")
async def health_check():
    """Health check do serviço"""
    return {
        "status": "healthy",
        "service": "BIUAI MCP Chatbot",
        "bot_name": BOT_NAME,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_message(request: ChatMessage):
    """Processar mensagem de chat"""
    try:
        # Gerar contexto
        context_prompt = prompt_system.get_context_prompt(request.context or {})
        
        # Buscar conhecimento relevante
        knowledge = knowledge_base.search_knowledge(request.message)
        
        # Construir prompt completo
        full_prompt = f"{context_prompt}\n"
        if knowledge:
            full_prompt += f"CONHECIMENTO RELEVANTE:\n{knowledge}\n\n"
        full_prompt += f"PERGUNTA DO USUÁRIO: {request.message}"
        
        # Gerar resposta
        response_text = await ollama_client.generate_response(
            prompt=full_prompt,
            system_prompt=prompt_system.system_prompt
        )
        
        # Salvar mensagens
        session_id = request.session_id or f"session_{request.user_id}_{datetime.now().timestamp()}"
        await chat_manager.save_message(session_id, request.user_id, request.message, False)
        await chat_manager.save_message(session_id, request.user_id, response_text, True)
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do chatbot")

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Obter histórico de chat"""
    try:
        history = await chat_manager.get_session_history(session_id)
        return {"session_id": session_id, "messages": history}
    except Exception as e:
        logger.error(f"Erro ao obter histórico: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter histórico")

@app.get("/config")
async def get_bot_config():
    """Obter configurações do bot"""
    return {
        "bot_name": BOT_NAME,
        "model": ollama_client.default_model,
        "features": [
            "Chat em tempo real",
            "Conhecimento especializado BIUAI",
            "Integração com dados do sistema",
            "Suporte a markdown",
            "Histórico de conversas"
        ]
    }

# WebSocket para chat em tempo real
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket para chat em tempo real"""
    await websocket.accept()
    await chat_manager.add_connection(session_id, websocket)
    
    try:
        while True:
            # Receber mensagem
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Processar como chat normal
            chat_request = ChatMessage(**message_data)
            response = await chat_message(chat_request)
            
            # Enviar resposta
            await websocket.send_text(response.model_dump_json())
            
    except WebSocketDisconnect:
        await chat_manager.remove_connection(session_id)
        logger.info(f"WebSocket desconectado: {session_id}")
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        await chat_manager.remove_connection(session_id)

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": f"🤖 {BOT_NAME}",
        "version": "1.0.0",
        "description": "Assistente Inteligente Especializado no Sistema BIUAI",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "websocket": "/ws/{session_id}",
            "history": "/chat/history/{session_id}",
            "config": "/config"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=MCP_SERVER_HOST,
        port=MCP_SERVER_PORT,
        reload=True,
        log_level="info"
    ) 