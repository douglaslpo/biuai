<template>
  <div class="chatbot-wrapper">
    <!-- Botão Flutuante do Chatbot - REDESIGN MODERNO -->
    <div
      v-if="!modalOpen"
      class="chatbot-fab-container"
      @click="toggleModal"
      :class="{ 'pulse-animation': hasNotification }"
    >
      <!-- Círculo principal com gradiente -->
      <div class="chatbot-fab-main">
        <!-- Ícone do robô -->
        <v-icon class="chatbot-icon" size="28">mdi-robot</v-icon>
        
        <!-- Badge de notificação -->
        <div v-if="hasNotification" class="notification-badge">
          {{ notificationCount }}
        </div>
        
        <!-- Ondas de animação -->
        <div class="wave-animation wave-1"></div>
        <div class="wave-animation wave-2"></div>
        <div class="wave-animation wave-3"></div>
      </div>
      
      <!-- Tooltip -->
      <div class="chatbot-tooltip">
        <div class="tooltip-content">
          🤖 {{ botConfig?.bot_name || 'Bi UAI Bot' }}
          <div class="tooltip-subtitle">Clique para conversar!</div>
        </div>
      </div>
    </div>

    <!-- Modal do Chatbot -->
    <v-dialog
      v-model="modalOpen"
      max-width="400"
      location="bottom end"
      class="chatbot-dialog"
      persistent
      transition="dialog-bottom-transition"
    >
      <v-card class="chatbot-card" height="600">
        <!-- Header do Chat -->
        <v-card-title class="chatbot-header pa-4">
          <div class="d-flex align-center justify-space-between w-100">
            <div class="d-flex align-center">
              <v-icon class="mr-2" color="white">mdi-robot</v-icon>
              <div>
                <div class="text-h6 text-white font-weight-bold">
                  {{ botConfig?.bot_name || 'Bi UAI Bot Administrador' }}
                </div>
                <div class="text-caption text-grey-lighten-1 d-flex align-center">
                  <v-icon 
                    :color="isOnline ? 'success' : 'grey'"
                    size="small"
                    class="mr-1"
                  >
                    mdi-circle
                  </v-icon>
                  {{ isOnline ? 'Online' : 'Offline' }}
                </div>
              </div>
            </div>
            <div class="d-flex">
              <v-btn
                icon="mdi-minus"
                variant="text"
                color="white"
                size="small"
                @click="minimizeChat"
                class="mr-1"
              >
                <v-tooltip activator="parent">Minimizar</v-tooltip>
              </v-btn>
              <v-btn
                icon="mdi-close"
                variant="text"
                color="white"
                size="small"
                @click="closeChat"
              >
                <v-tooltip activator="parent">Fechar</v-tooltip>
              </v-btn>
            </div>
          </div>
        </v-card-title>

        <!-- Área de Mensagens -->
        <v-card-text class="chatbot-messages pa-0" ref="messagesContainer">
          <!-- Mensagem de Boas-vindas -->
          <div v-if="messages.length === 0" class="welcome-section pa-4">
            <div class="d-flex flex-column align-center mb-4">
              <v-avatar size="60" color="primary" class="mb-3">
                <v-icon size="30" color="white">mdi-robot</v-icon>
              </v-avatar>
              <div class="text-center">
                <h6 class="text-h6 mb-2">{{ welcomeMessage }}</h6>
                <p class="text-body-2 text-grey-darken-1 mb-4">
                  Sou especialista no sistema BIUAI e posso te ajudar com qualquer dúvida!
                </p>
              </div>
            </div>
            
            <!-- Ações Rápidas -->
            <div class="quick-actions d-flex flex-wrap ga-2">
              <v-btn
                v-for="action in quickActions"
                :key="action.title"
                variant="outlined"
                color="primary"
                size="small"
                rounded
                @click="sendQuickAction(action.action)"
                class="text-none"
              >
                <v-icon start size="small">{{ action.icon }}</v-icon>
                {{ action.title }}
              </v-btn>
            </div>
          </div>

          <!-- Lista de Mensagens -->
          <div class="messages-list pa-3">
            <div
              v-for="(message, index) in messages"
              :key="index"
              class="message-item mb-4"
              :class="{ 'user-message': !message.is_bot, 'bot-message': message.is_bot }"
            >
              <!-- Mensagem do Bot -->
              <div v-if="message.is_bot" class="d-flex align-start mb-2">
                <v-avatar size="35" color="primary" class="mr-3 flex-shrink-0">
                  <v-icon color="white">mdi-robot</v-icon>
                </v-avatar>
                <div class="flex-grow-1">
                  <v-card variant="outlined" class="bot-message-card pa-3">
                    <div class="message-text" v-html="formatMessage(message.message)"></div>
                    <div class="d-flex align-center justify-space-between mt-2">
                      <span class="text-caption text-grey-darken-1">
                        {{ formatTime(message.timestamp) }}
                      </span>
                      <div class="d-flex">
                        <v-btn
                          icon="mdi-thumb-up"
                          variant="text"
                          size="small"
                          :color="message.helpful === true ? 'success' : 'grey'"
                          @click="rateBotMessage(index, true)"
                        >
                          <v-tooltip activator="parent">Útil</v-tooltip>
                        </v-btn>
                        <v-btn
                          icon="mdi-thumb-down"
                          variant="text"
                          size="small"
                          :color="message.helpful === false ? 'error' : 'grey'"
                          @click="rateBotMessage(index, false)"
                        >
                          <v-tooltip activator="parent">Não útil</v-tooltip>
                        </v-btn>
                        <v-btn
                          icon="mdi-content-copy"
                          variant="text"
                          size="small"
                          color="grey"
                          @click="copyMessage(message.message)"
                        >
                          <v-tooltip activator="parent">Copiar</v-tooltip>
                        </v-btn>
                      </div>
                    </div>
                    
                    <!-- Sugestões -->
                    <div v-if="message.suggestions && message.suggestions.length > 0" class="mt-3">
                      <v-chip
                        v-for="suggestion in message.suggestions"
                        :key="suggestion"
                        color="primary"
                        variant="outlined"
                        size="small"
                        class="mr-2 mb-1"
                        @click="sendSuggestion(suggestion)"
                        clickable
                      >
                        {{ suggestion }}
                      </v-chip>
                    </div>
                  </v-card>
                </div>
              </div>

              <!-- Mensagem do Usuário -->
              <div v-else class="d-flex align-start justify-end mb-2">
                <div class="flex-grow-1 text-right mr-3">
                  <v-card color="primary" class="user-message-card pa-3">
                    <div class="message-text text-white">{{ message.message }}</div>
                    <div class="text-caption text-grey-lighten-2 mt-1">
                      {{ formatTime(message.timestamp) }}
                    </div>
                  </v-card>
                </div>
                <v-avatar size="35" color="secondary" class="flex-shrink-0">
                  <v-icon color="white">mdi-account</v-icon>
                </v-avatar>
              </div>
            </div>

            <!-- Indicador de Digitação -->
            <div v-if="isTyping" class="d-flex align-start mb-2">
              <v-avatar size="35" color="primary" class="mr-3">
                <v-icon color="white">mdi-robot</v-icon>
              </v-avatar>
              <v-card variant="outlined" class="pa-3">
                <div class="typing-indicator d-flex align-center">
                  <span class="text-body-2 mr-2">Digitando</span>
                  <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </v-card>
            </div>
          </div>
        </v-card-text>

        <!-- Input de Mensagem -->
        <v-card-actions class="pa-3">
          <div class="d-flex w-100">
            <v-text-field
              v-model="currentMessage"
              placeholder="Digite sua mensagem..."
              variant="outlined"
              density="compact"
              hide-details
              @keydown.enter="sendMessage"
              :disabled="isTyping"
              class="mr-2"
            >
              <template v-slot:prepend-inner>
                <v-btn
                  icon="mdi-attachment"
                  variant="text"
                  size="small"
                  @click="showAttachmentMenu = !showAttachmentMenu"
                >
                  <v-tooltip activator="parent">Anexar</v-tooltip>
                </v-btn>
              </template>
            </v-text-field>
            <v-btn
              icon="mdi-send"
              color="primary"
              @click="sendMessage"
              :disabled="!currentMessage.trim() || isTyping"
              :loading="isTyping"
            >
              <v-tooltip activator="parent">Enviar</v-tooltip>
            </v-btn>
          </div>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { chatbotService } from '@/services/chatbot'

// Stores
const authStore = useAuthStore()

// Data
const modalOpen = ref(false)
const currentMessage = ref('')
const messages = ref([])
const isTyping = ref(false)
const sessionId = ref(null)
const hasNotification = ref(false)
const notificationCount = ref(0)
const showAttachmentMenu = ref(false)
const messagesContainer = ref(null)

// Bot Config
const botConfig = ref({
  bot_name: 'Bi UAI Bot Administrador',
  personality: 'helpful',
  language: 'pt-BR'
})

// Computed
const isOnline = computed(() => true) // Simular online sempre
const welcomeMessage = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Bom dia! 😊'
  if (hour < 18) return 'Boa tarde! 😊'
  return 'Boa noite! 😊'
})

const quickActions = computed(() => [
  { title: 'Como usar', icon: 'mdi-help', action: 'Como usar o sistema BIUAI?' },
  { title: 'Dashboard', icon: 'mdi-view-dashboard', action: 'Como funciona o dashboard?' },
  { title: 'Lançamentos', icon: 'mdi-cash-multiple', action: 'Como fazer lançamentos?' },
  { title: 'Relatórios', icon: 'mdi-chart-line', action: 'Como gerar relatórios?' }
])

// Methods
const toggleModal = () => {
  modalOpen.value = !modalOpen.value
  if (modalOpen.value) {
    generateSessionId()
    loadBotConfig()
    hasNotification.value = false
    notificationCount.value = 0
  }
}

const minimizeChat = () => {
  modalOpen.value = false
}

const closeChat = () => {
  modalOpen.value = false
  // Opcional: limpar sessão
}

const generateSessionId = () => {
  sessionId.value = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

const loadBotConfig = async () => {
  try {
    const config = await chatbotService.getBotConfig()
    botConfig.value = { ...botConfig.value, ...config }
  } catch (error) {
    console.warn('Erro ao carregar configuração do bot:', error)
  }
}

const sendMessage = async () => {
  if (!currentMessage.value.trim() || isTyping.value) return

  const userMessage = {
    message: currentMessage.value,
    is_bot: false,
    timestamp: new Date(),
    session_id: sessionId.value
  }

  messages.value.push(userMessage)
  const messageText = currentMessage.value
  currentMessage.value = ''
  isTyping.value = true

  // Scroll para baixo
  await nextTick()
  scrollToBottom()

  try {
    const response = await chatbotService.sendMessage({
      message: messageText,
      session_id: sessionId.value,
      context: {
        user_id: authStore.user?.id,
        page: window.location.pathname
      }
    })

    const botMessage = {
      message: response.message,
      is_bot: true,
      timestamp: new Date(),
      session_id: sessionId.value,
      suggestions: response.suggestions || []
    }

    messages.value.push(botMessage)

    // Scroll para baixo
    await nextTick()
    scrollToBottom()

  } catch (error) {
    console.error('Erro ao enviar mensagem:', error)
    const errorMessage = {
      message: 'Desculpe, ocorreu um erro. Tente novamente em alguns instantes.',
      is_bot: true,
      timestamp: new Date(),
      session_id: sessionId.value
    }
    messages.value.push(errorMessage)
  } finally {
    isTyping.value = false
  }
}

const sendQuickAction = (action) => {
  currentMessage.value = action
  sendMessage()
}

const sendSuggestion = (suggestion) => {
  currentMessage.value = suggestion
  sendMessage()
}

const rateBotMessage = async (messageIndex, helpful) => {
  const message = messages.value[messageIndex]
  if (message && message.is_bot) {
    message.helpful = helpful
    
    try {
      await chatbotService.sendFeedback({
        session_id: sessionId.value,
        message_index: messageIndex,
        helpful: helpful,
        rating: helpful ? 5 : 2
      })
    } catch (error) {
      console.error('Erro ao enviar feedback:', error)
    }
  }
}

const copyMessage = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    // Mostrar feedback de cópia (opcional)
  })
}

const formatMessage = (message) => {
  // Formatação básica de markdown
  return message
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    const container = messagesContainer.value.$el || messagesContainer.value
    container.scrollTop = container.scrollHeight
  }
}

// Lifecycle
onMounted(() => {
  // Simular notificação inicial
  setTimeout(() => {
    hasNotification.value = true
    notificationCount.value = 1
  }, 3000)
})

// Watchers
watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })
</script>

<style scoped>
/* ========== NOVO DESIGN DO ÍCONE CHATBOT ========== */
.chatbot-fab-container {
  position: fixed;
  bottom: 25px;
  right: 25px;
  z-index: 9999;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.chatbot-fab-main {
  position: relative;
  width: 65px;
  height: 65px;
  background: linear-gradient(135deg, #1976d2, #42a5f5, #03dac6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 8px 25px rgba(25, 118, 210, 0.3),
    0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 3px solid rgba(255, 255, 255, 0.2);
}

.chatbot-fab-container:hover .chatbot-fab-main {
  transform: scale(1.1) translateY(-2px);
  box-shadow: 
    0 12px 35px rgba(25, 118, 210, 0.4),
    0 6px 20px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, #1565c0, #2196f3, #00bcd4);
}

.chatbot-icon {
  color: white !important;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Animação de pulso para notificações */
.pulse-animation .chatbot-fab-main {
  animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    transform: scale(1);
    box-shadow: 
      0 8px 25px rgba(25, 118, 210, 0.3),
      0 4px 12px rgba(0, 0, 0, 0.15);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 
      0 0 0 15px rgba(25, 118, 210, 0),
      0 0 0 30px rgba(25, 118, 210, 0),
      0 8px 25px rgba(25, 118, 210, 0.4);
  }
}

/* Badge de notificação */
.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: linear-gradient(135deg, #f44336, #ff5722);
  color: white;
  border-radius: 12px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: bold;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.4);
  animation: bounce-in 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes bounce-in {
  0% { transform: scale(0); opacity: 0; }
  60% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(1); }
}

/* Ondas de animação */
.wave-animation {
  position: absolute;
  border: 2px solid rgba(25, 118, 210, 0.3);
  border-radius: 50%;
  animation: wave-expand 3s infinite;
}

.wave-1 {
  width: 65px;
  height: 65px;
  animation-delay: 0s;
}

.wave-2 {
  width: 65px;
  height: 65px;
  animation-delay: 1s;
}

.wave-3 {
  width: 65px;
  height: 65px;
  animation-delay: 2s;
}

@keyframes wave-expand {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

/* Tooltip moderno */
.chatbot-tooltip {
  position: absolute;
  right: 75px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  color: white;
  padding: 12px 16px;
  border-radius: 12px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.chatbot-tooltip::after {
  content: '';
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  border: 8px solid transparent;
  border-left-color: rgba(0, 0, 0, 0.85);
}

.chatbot-fab-container:hover .chatbot-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translateY(-50%) translateX(-8px);
}

.tooltip-content {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
}

.tooltip-subtitle {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 2px;
}

/* Responsive */
@media (max-width: 768px) {
  .chatbot-fab-container {
    bottom: 20px;
    right: 20px;
  }
  
  .chatbot-fab-main {
    width: 58px;
    height: 58px;
  }
  
  .chatbot-icon {
    font-size: 24px !important;
  }
  
  .chatbot-tooltip {
    display: none; /* Ocultar tooltip em mobile */
  }
}

/* ========== ESTILOS EXISTENTES ========== */
.chatbot-wrapper {
  position: relative;
}

.chatbot-dialog {
  position: fixed !important;
  bottom: 100px !important;
  right: 20px !important;
}

.chatbot-card {
  border-radius: 16px !important;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2) !important;
}

.chatbot-header {
  background: linear-gradient(135deg, #1976d2, #1565c0) !important;
  border-bottom: none !important;
}

.chatbot-messages {
  height: 400px;
  overflow-y: auto;
  background: #f8f9fa;
}

.messages-list {
  min-height: 100%;
}

.bot-message-card {
  background: white;
  border-left: 4px solid #1976D2;
}

.user-message-card {
  border-radius: 16px 16px 4px 16px !important;
  max-width: 85%;
}

.welcome-section {
  text-align: center;
  padding: 32px 16px;
}

.quick-actions {
  margin-top: 16px;
}

.typing-indicator {
  padding: 8px 12px;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #1976D2;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: 0s; }
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 80%, 100% { 
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% { 
    transform: scale(1);
    opacity: 1;
  }
}

/* Scrollbar personalizada */
.chatbot-messages::-webkit-scrollbar {
  width: 6px;
}

.chatbot-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chatbot-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chatbot-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsividade */
@media (max-width: 600px) {
  .chatbot-dialog {
    right: 10px !important;
    bottom: 80px !important;
  }
  
  .chatbot-card {
    width: calc(100vw - 20px);
    max-width: 380px;
  }
}
</style> 