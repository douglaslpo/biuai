/**
 * Serviço para comunicação com a API do Chatbot
 */

import axios from 'axios'
import { useAuthStore } from '../stores/auth'

// URL direta para o MCP Chatbot Service
const CHATBOT_API_URL = process.env.VUE_APP_CHATBOT_URL || 'http://localhost:8002'

class ChatbotService {
  constructor() {
    this.apiClient = axios.create({
      baseURL: CHATBOT_API_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // Interceptador para adicionar token de autenticação
    this.apiClient.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore()
        const token = authStore.token
        
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Interceptador para tratamento de erros
    this.apiClient.interceptors.response.use(
      (response) => {
        return response.data
      },
      (error) => {
        console.error('Erro na API do Chatbot:', error)
        
        if (error.response?.status === 401) {
          // Token expirado - redirecionar para login
          const authStore = useAuthStore()
          authStore.logout()
        }
        
        return Promise.reject(this.formatError(error))
      }
    )
  }

  /**
   * Formatar erro para exibição
   */
  formatError(error) {
    if (error.response?.data?.detail) {
      return new Error(error.response.data.detail)
    }
    
    if (error.response?.data?.message) {
      return new Error(error.response.data.message)
    }
    
    if (error.message) {
      return new Error(error.message)
    }
    
    return new Error('Erro desconhecido no chatbot')
  }

  /**
   * Enviar mensagem para o chatbot
   */
  async sendMessage({ message, session_id = null, context = {} }) {
    try {
      const authStore = useAuthStore()
      const user = authStore.user
      
      const payload = {
        message: message.trim(),
        user_id: user?.id?.toString() || "1",
        session_id: session_id || this.generateSessionId(),
        context: {
          ...context,
          timestamp: new Date().toISOString(),
          user_agent: navigator.userAgent,
          current_url: window.location.href
        }
      }

      const response = await this.apiClient.post('/chat', payload)
      
      return {
        message: response.response,
        session_id: response.session_id,
        timestamp: response.timestamp,
        bot_name: response.bot_name,
        suggestions: response.suggestions || []
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error)
      throw error
    }
  }

  /**
   * Obter histórico de uma sessão de chat
   */
  async getChatHistory(sessionId) {
    try {
      const response = await this.apiClient.get(`/chat/history/${sessionId}`)
      
      return {
        session_id: response.session_id,
        messages: response.messages || [],
        created_at: response.created_at,
        updated_at: response.updated_at
      }
    } catch (error) {
      console.error('Erro ao obter histórico:', error)
      // Retornar histórico vazio em caso de erro
      return {
        session_id: sessionId,
        messages: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    }
  }

  /**
   * Obter configurações do bot
   */
  async getBotConfig() {
    try {
      const response = await this.apiClient.get('/config')
      
      return {
        bot_name: response.bot_name || 'Bi UAI Bot Administrador',
        model: response.model,
        features: response.features || [],
        personality: response.personality,
        system_prompt: response.system_prompt,
        enabled: response.enabled !== false
      }
    } catch (error) {
      console.error('Erro ao obter configuração do bot:', error)
      
      // Retornar configuração padrão
      return {
        bot_name: 'Bi UAI Bot Administrador',
        model: 'llama3.2:3b',
        features: ['Chat em tempo real', 'Conhecimento especializado'],
        personality: 'amigável e profissional',
        enabled: true
      }
    }
  }

  /**
   * Verificar saúde do serviço de chatbot
   */
  async healthCheck() {
    try {
      const response = await this.apiClient.get('/health')
      
      return {
        status: response.status,
        service: response.service,
        bot_name: response.bot_name,
        timestamp: response.timestamp
      }
    } catch (error) {
      console.error('Health check do chatbot falhou:', error)
      
      return {
        status: 'unhealthy',
        service: 'chatbot',
        error: error.message,
        timestamp: new Date().toISOString()
      }
    }
  }

  /**
   * Enviar feedback sobre o chatbot
   */
  async sendFeedback({ session_id, message_index, helpful, rating = 5 }) {
    try {
      const payload = {
        session_id,
        message_index,
        rating: Math.max(1, Math.min(5, rating)), // Garantir que está entre 1-5
        helpful
      }

      const response = await this.apiClient.post('/feedback', payload)
      
      return {
        status: response.status,
        message: response.message || 'Feedback enviado com sucesso'
      }
    } catch (error) {
      console.error('Erro ao enviar feedback:', error)
      throw error
    }
  }

  /**
   * Obter contexto do usuário
   */
  async getUserContext() {
    try {
      const response = await this.apiClient.get('/context')
      
      return {
        user_id: response.user_id,
        current_page: response.current_page,
        recent_actions: response.recent_actions || [],
        financial_summary: response.financial_summary || {},
        preferences: response.preferences || {},
        timestamp: response.timestamp
      }
    } catch (error) {
      console.error('Erro ao obter contexto do usuário:', error)
      
      // Retornar contexto básico
      return {
        user_id: 'unknown',
        current_page: window.location.pathname,
        recent_actions: [],
        financial_summary: {},
        preferences: {},
        timestamp: new Date().toISOString()
      }
    }
  }

  /**
   * Obter sugestões de perguntas
   */
  async getSuggestions(query = '') {
    try {
      const params = query.trim() ? { query } : {}
      const response = await this.apiClient.get('/suggestions', { params })
      
      return {
        query: response.query,
        suggestions: response.suggestions || [],
        timestamp: response.timestamp
      }
    } catch (error) {
      console.error('Erro ao obter sugestões:', error)
      
      // Retornar sugestões padrão
      return {
        query,
        suggestions: [
          'Como usar o dashboard?',
          'Como adicionar lançamentos?',
          'Como criar relatórios?',
          'Como categorizar transações?',
          'Como definir metas financeiras?'
        ],
        timestamp: new Date().toISOString()
      }
    }
  }

  /**
   * Obter ajuda rápida e ações comuns
   */
  async getQuickHelp() {
    try {
      const response = await this.apiClient.get('/quick-help')
      
      return {
        welcome_message: response.welcome_message,
        common_actions: response.common_actions || [],
        tips: response.tips || []
      }
    } catch (error) {
      console.error('Erro ao obter ajuda rápida:', error)
      
      // Retornar ajuda padrão
      return {
        welcome_message: 'Olá! Sou o Bi UAI Bot Administrador. Como posso te ajudar hoje?',
        common_actions: [
          {
            title: 'Ver Dashboard',
            description: 'Acesse sua visão geral financeira',
            action: 'Como acessar o dashboard?',
            icon: 'dashboard'
          },
          {
            title: 'Adicionar Lançamento',
            description: 'Registre uma nova receita ou despesa',
            action: 'Como adicionar um novo lançamento?',
            icon: 'add_circle'
          },
          {
            title: 'Ver Relatórios',
            description: 'Analise seus dados financeiros',
            action: 'Como gerar relatórios?',
            icon: 'analytics'
          },
          {
            title: 'Configurar Categorias',
            description: 'Organize suas transações',
            action: 'Como configurar categorias?',
            icon: 'category'
          }
        ],
        tips: [
          'Use comandos como "mostrar gastos deste mês" para consultas específicas',
          'Posso ajudar com navegação e explicações de funcionalidades',
          'Digite sua dúvida em linguagem natural, entendo português brasileiro!'
        ]
      }
    }
  }

  /**
   * MÉTODOS ADMINISTRATIVOS (apenas para admins)
   */

  /**
   * Obter analytics do chatbot (apenas admins)
   */
  async getAnalytics() {
    try {
      const response = await this.apiClient.get('/admin/analytics')
      
      return {
        total_sessions: response.total_sessions,
        total_messages: response.total_messages,
        avg_session_duration: response.avg_session_duration,
        most_common_questions: response.most_common_questions || [],
        user_satisfaction: response.user_satisfaction,
        response_time_avg: response.response_time_avg
      }
    } catch (error) {
      console.error('Erro ao obter analytics:', error)
      throw error
    }
  }

  /**
   * Obter todas as sessões de chat (apenas admins)
   */
  async getAdminSessions(limit = 20, offset = 0) {
    try {
      const response = await this.apiClient.get('/admin/sessions', {
        params: { limit, offset }
      })
      
      return {
        sessions: response.sessions || [],
        total: response.total,
        limit: response.limit,
        offset: response.offset
      }
    } catch (error) {
      console.error('Erro ao obter sessões:', error)
      throw error
    }
  }

  /**
   * Enviar mensagem broadcast (apenas admins)
   */
  async sendBroadcast(message) {
    try {
      const response = await this.apiClient.post('/admin/broadcast', {
        message: message.trim()
      })
      
      return {
        status: response.status,
        message: response.message,
        recipients: response.recipients,
        content: response.content
      }
    } catch (error) {
      console.error('Erro ao enviar broadcast:', error)
      throw error
    }
  }

  /**
   * UTILITÁRIOS
   */

  /**
   * Conectar WebSocket para chat em tempo real
   */
  connectWebSocket(sessionId, onMessage, onError = null) {
    const wsUrl = `${CHATBOT_API_URL.replace('http', 'ws')}/ws/${sessionId}`
    
    try {
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log('WebSocket conectado')
      }
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          onMessage(message)
        } catch (error) {
          console.error('Erro ao processar mensagem WebSocket:', error)
        }
      }
      
      ws.onerror = (error) => {
        console.error('Erro WebSocket:', error)
        if (onError) onError(error)
      }
      
      ws.onclose = () => {
        console.log('WebSocket desconectado')
      }
      
      return ws
    } catch (error) {
      console.error('Erro ao conectar WebSocket:', error)
      if (onError) onError(error)
      return null
    }
  }

  /**
   * Gerar ID único para sessão
   */
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * Validar mensagem antes de enviar
   */
  validateMessage(message) {
    if (!message || typeof message !== 'string') {
      throw new Error('Mensagem deve ser uma string não vazia')
    }
    
    const trimmed = message.trim()
    
    if (trimmed.length === 0) {
      throw new Error('Mensagem não pode estar vazia')
    }
    
    if (trimmed.length > 2000) {
      throw new Error('Mensagem muito longa (máximo 2000 caracteres)')
    }
    
    return trimmed
  }

  /**
   * Formatar timestamp para exibição
   */
  formatTimestamp(timestamp) {
    try {
      const date = new Date(timestamp)
      
      return {
        time: date.toLocaleTimeString('pt-BR', {
          hour: '2-digit',
          minute: '2-digit'
        }),
        date: date.toLocaleDateString('pt-BR'),
        relative: this.getRelativeTime(date)
      }
    } catch (error) {
      return {
        time: '--:--',
        date: '--/--/----',
        relative: 'agora'
      }
    }
  }

  /**
   * Obter tempo relativo
   */
  getRelativeTime(date) {
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'agora'
    if (diffMins < 60) return `${diffMins}m`
    
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h`
    
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d`
  }
}

// Exportar instância única
export const chatbotService = new ChatbotService()

// Exportar classe para casos específicos
export default ChatbotService 