<template>
  <q-page class="chatbot-admin-page">
    <!-- Header da Página -->
    <div class="page-header">
      <div class="row items-center justify-between">
        <div class="col">
          <h4 class="page-title">
            <q-icon name="smart_toy" class="q-mr-sm" />
            Administração do Chatbot
          </h4>
          <p class="page-subtitle">
            Gerencie configurações e monitore o desempenho do Bi UAI Bot Administrador
          </p>
        </div>
        <div class="col-auto">
          <q-btn
            color="primary"
            icon="refresh"
            label="Atualizar Dados"
            @click="refreshData"
            :loading="refreshing"
          />
        </div>
      </div>
    </div>

    <!-- Status Cards -->
    <div class="status-cards">
      <div class="row q-gutter-md">
        <!-- Status do Bot -->
        <div class="col-12 col-md-3">
          <q-card class="status-card">
            <q-card-section>
              <div class="status-content">
                <q-icon 
                  :name="botStatus.online ? 'check_circle' : 'error'" 
                  :color="botStatus.online ? 'green' : 'red'"
                  size="2rem"
                />
                <div class="status-text">
                  <div class="status-label">Status do Bot</div>
                  <div class="status-value">
                    {{ botStatus.online ? 'Online' : 'Offline' }}
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Total de Sessões -->
        <div class="col-12 col-md-3">
          <q-card class="status-card">
            <q-card-section>
              <div class="status-content">
                <q-icon name="chat" color="blue" size="2rem" />
                <div class="status-text">
                  <div class="status-label">Total de Sessões</div>
                  <div class="status-value">{{ analytics.total_sessions || 0 }}</div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Satisfação do Usuário -->
        <div class="col-12 col-md-3">
          <q-card class="status-card">
            <q-card-section>
              <div class="status-content">
                <q-icon name="sentiment_satisfied" color="orange" size="2rem" />
                <div class="status-text">
                  <div class="status-label">Satisfação</div>
                  <div class="status-value">
                    {{ analytics.user_satisfaction || 0 }}/10
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Tempo de Resposta -->
        <div class="col-12 col-md-3">
          <q-card class="status-card">
            <q-card-section>
              <div class="status-content">
                <q-icon name="timer" color="purple" size="2rem" />
                <div class="status-text">
                  <div class="status-label">Tempo Médio</div>
                  <div class="status-value">
                    {{ analytics.response_time_avg || 0 }}s
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Tabs de Administração -->
    <q-tabs
      v-model="activeTab"
      class="admin-tabs"
      dense
      active-color="primary"
      indicator-color="primary"
      align="justify"
    >
      <q-tab name="config" icon="settings" label="Configurações" />
      <q-tab name="analytics" icon="analytics" label="Analytics" />
      <q-tab name="sessions" icon="history" label="Sessões" />
      <q-tab name="knowledge" icon="school" label="Base de Conhecimento" />
      <q-tab name="logs" icon="description" label="Logs" />
    </q-tabs>

    <q-tab-panels v-model="activeTab" animated class="admin-panels">
      <!-- Configurações -->
      <q-tab-panel name="config" class="q-pa-md">
        <div class="config-section">
          <h5>Configurações do Bot</h5>
          
          <div class="row q-gutter-lg">
            <!-- Configurações Gerais -->
            <div class="col-12 col-md-6">
              <q-card class="config-card">
                <q-card-section>
                  <h6>Configurações Gerais</h6>
                  
                  <q-form @submit="saveConfig">
                    <q-input
                      v-model="botConfig.bot_name"
                      label="Nome do Bot"
                      outlined
                      dense
                      class="q-mb-md"
                    />
                    
                    <q-input
                      v-model="botConfig.personality"
                      label="Personalidade"
                      type="textarea"
                      outlined
                      dense
                      rows="3"
                      class="q-mb-md"
                    />
                    
                    <q-input
                      v-model="botConfig.model_name"
                      label="Modelo de IA"
                      outlined
                      dense
                      readonly
                      class="q-mb-md"
                    />
                    
                    <div class="row q-gutter-md q-mb-md">
                      <div class="col">
                        <q-input
                          v-model.number="botConfig.temperature"
                          label="Temperatura"
                          type="number"
                          min="0"
                          max="2"
                          step="0.1"
                          outlined
                          dense
                        />
                      </div>
                      <div class="col">
                        <q-input
                          v-model.number="botConfig.max_tokens"
                          label="Max Tokens"
                          type="number"
                          min="100"
                          max="4000"
                          outlined
                          dense
                        />
                      </div>
                    </div>
                    
                    <q-toggle
                      v-model="botConfig.enabled"
                      label="Bot Habilitado"
                      color="primary"
                      class="q-mb-md"
                    />
                    
                    <div class="config-actions">
                      <q-btn
                        type="submit"
                        color="primary"
                        label="Salvar Configurações"
                        :loading="savingConfig"
                      />
                      <q-btn
                        flat
                        color="grey"
                        label="Restaurar Padrão"
                        @click="resetConfig"
                        class="q-ml-sm"
                      />
                    </div>
                  </q-form>
                </q-card-section>
              </q-card>
            </div>

            <!-- Prompt do Sistema -->
            <div class="col-12 col-md-6">
              <q-card class="config-card">
                <q-card-section>
                  <h6>Prompt do Sistema</h6>
                  
                  <q-input
                    v-model="botConfig.system_prompt"
                    type="textarea"
                    label="Prompt do Sistema"
                    outlined
                    rows="15"
                    class="q-mb-md"
                  />
                  
                  <div class="prompt-actions">
                    <q-btn
                      color="secondary"
                      label="Testar Prompt"
                      @click="testPrompt"
                      :loading="testingPrompt"
                    />
                    <q-btn
                      flat
                      color="grey"
                      label="Prompt Padrão"
                      @click="resetPrompt"
                      class="q-ml-sm"
                    />
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
      </q-tab-panel>

      <!-- Analytics -->
      <q-tab-panel name="analytics" class="q-pa-md">
        <div class="analytics-section">
          <h5>Analytics do Chatbot</h5>
          
          <div class="row q-gutter-lg">
            <!-- Métricas Gerais -->
            <div class="col-12 col-md-6">
              <q-card class="analytics-card">
                <q-card-section>
                  <h6>Métricas de Uso</h6>
                  
                  <div class="metrics-list">
                    <div class="metric-item">
                      <span class="metric-label">Total de Sessões:</span>
                      <span class="metric-value">{{ analytics.total_sessions || 0 }}</span>
                    </div>
                    <div class="metric-item">
                      <span class="metric-label">Total de Mensagens:</span>
                      <span class="metric-value">{{ analytics.total_messages || 0 }}</span>
                    </div>
                    <div class="metric-item">
                      <span class="metric-label">Duração Média da Sessão:</span>
                      <span class="metric-value">{{ analytics.avg_session_duration || 0 }} min</span>
                    </div>
                    <div class="metric-item">
                      <span class="metric-label">Tempo de Resposta Médio:</span>
                      <span class="metric-value">{{ analytics.response_time_avg || 0 }}s</span>
                    </div>
                    <div class="metric-item">
                      <span class="metric-label">Satisfação do Usuário:</span>
                      <span class="metric-value">
                        {{ analytics.user_satisfaction || 0 }}/10
                        <q-icon 
                          :name="analytics.user_satisfaction >= 7 ? 'sentiment_satisfied' : 'sentiment_neutral'"
                          :color="analytics.user_satisfaction >= 7 ? 'green' : 'orange'"
                        />
                      </span>
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Perguntas Mais Comuns -->
            <div class="col-12 col-md-6">
              <q-card class="analytics-card">
                <q-card-section>
                  <h6>Perguntas Mais Comuns</h6>
                  
                  <q-list>
                    <q-item
                      v-for="(question, index) in analytics.most_common_questions"
                      :key="index"
                    >
                      <q-item-section avatar>
                        <q-avatar color="primary" text-color="white" size="sm">
                          {{ index + 1 }}
                        </q-avatar>
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>{{ question }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <!-- Gráfico de Atividade -->
          <div class="row q-mt-lg">
            <div class="col-12">
              <q-card class="analytics-card">
                <q-card-section>
                  <h6>Atividade do Bot (Últimos 7 dias)</h6>
                  <div class="chart-placeholder">
                    <p class="text-grey-6 text-center">
                      Gráfico de atividade em desenvolvimento
                    </p>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
      </q-tab-panel>

      <!-- Sessões -->
      <q-tab-panel name="sessions" class="q-pa-md">
        <div class="sessions-section">
          <div class="row items-center justify-between q-mb-md">
            <div class="col">
              <h5>Sessões de Chat</h5>
            </div>
            <div class="col-auto">
              <q-btn
                color="primary"
                icon="refresh"
                label="Atualizar"
                @click="loadSessions"
                :loading="loadingSessions"
              />
            </div>
          </div>
          
          <q-card class="sessions-card">
            <q-card-section>
              <q-table
                :columns="sessionsColumns"
                :rows="sessions"
                :loading="loadingSessions"
                row-key="session_id"
                :pagination="sessionsPagination"
                @request="onSessionsRequest"
              >
                <template v-slot:body-cell-status="props">
                  <q-td :props="props">
                    <q-badge
                      :color="props.row.active ? 'green' : 'grey'"
                      :label="props.row.active ? 'Ativa' : 'Inativa'"
                    />
                  </q-td>
                </template>
                
                <template v-slot:body-cell-actions="props">
                  <q-td :props="props">
                    <q-btn
                      flat
                      round
                      dense
                      icon="visibility"
                      color="primary"
                      @click="viewSession(props.row)"
                    >
                      <q-tooltip>Ver Sessão</q-tooltip>
                    </q-btn>
                    <q-btn
                      flat
                      round
                      dense
                      icon="delete"
                      color="red"
                      @click="deleteSession(props.row)"
                    >
                      <q-tooltip>Excluir</q-tooltip>
                    </q-btn>
                  </q-td>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </div>
      </q-tab-panel>

      <!-- Base de Conhecimento -->
      <q-tab-panel name="knowledge" class="q-pa-md">
        <div class="knowledge-section">
          <div class="row items-center justify-between q-mb-md">
            <div class="col">
              <h5>Base de Conhecimento</h5>
            </div>
            <div class="col-auto">
              <q-btn
                color="primary"
                icon="add"
                label="Adicionar Item"
                @click="addKnowledgeItem"
              />
            </div>
          </div>
          
          <div class="row q-gutter-md">
            <!-- Categorias -->
            <div class="col-12 col-md-4">
              <q-card class="knowledge-card">
                <q-card-section>
                  <h6>Categorias</h6>
                  <q-list>
                    <q-item
                      v-for="category in knowledgeCategories"
                      :key="category.name"
                      clickable
                      @click="selectCategory(category)"
                      :active="selectedCategory === category.name"
                    >
                      <q-item-section avatar>
                        <q-icon :name="category.icon" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>{{ category.label }}</q-item-label>
                        <q-item-label caption>{{ category.count }} itens</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </div>

            <!-- Itens de Conhecimento -->
            <div class="col-12 col-md-8">
              <q-card class="knowledge-card">
                <q-card-section>
                  <h6>{{ selectedCategoryLabel }}</h6>
                  
                  <q-list>
                    <q-item
                      v-for="item in knowledgeItems"
                      :key="item.id"
                    >
                      <q-item-section>
                        <q-item-label>{{ item.title }}</q-item-label>
                        <q-item-label caption>{{ item.content.substring(0, 100) }}...</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <div class="item-actions">
                          <q-btn
                            flat
                            round
                            dense
                            icon="edit"
                            color="primary"
                            @click="editKnowledgeItem(item)"
                          />
                          <q-btn
                            flat
                            round
                            dense
                            icon="delete"
                            color="red"
                            @click="deleteKnowledgeItem(item)"
                          />
                        </div>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
      </q-tab-panel>

      <!-- Logs -->
      <q-tab-panel name="logs" class="q-pa-md">
        <div class="logs-section">
          <div class="row items-center justify-between q-mb-md">
            <div class="col">
              <h5>Logs do Sistema</h5>
            </div>
            <div class="col-auto">
              <q-btn
                color="primary"
                icon="refresh"
                label="Atualizar Logs"
                @click="loadLogs"
                :loading="loadingLogs"
              />
            </div>
          </div>
          
          <q-card class="logs-card">
            <q-card-section>
              <div class="logs-content">
                <pre v-if="logs" class="logs-text">{{ logs }}</pre>
                <div v-else class="text-center text-grey-6">
                  <q-icon name="description" size="3rem" />
                  <p>Nenhum log disponível</p>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </q-tab-panel>
    </q-tab-panels>

    <!-- Modal de Teste de Prompt -->
    <q-dialog v-model="testPromptModal">
      <q-card style="min-width: 500px">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Testar Prompt</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        
        <q-card-section>
          <q-input
            v-model="testMessage"
            label="Mensagem de teste"
            type="textarea"
            outlined
            rows="3"
            class="q-mb-md"
          />
          
          <q-btn
            color="primary"
            label="Testar"
            @click="runPromptTest"
            :loading="testingPrompt"
            class="q-mb-md"
          />
          
          <div v-if="testResponse" class="test-response">
            <h6>Resposta:</h6>
            <div class="response-content" v-html="testResponse"></div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Modal de Broadcast -->
    <q-dialog v-model="broadcastModal">
      <q-card style="min-width: 400px">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Enviar Broadcast</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        
        <q-card-section>
          <q-input
            v-model="broadcastMessage"
            label="Mensagem para todos os usuários"
            type="textarea"
            outlined
            rows="4"
            class="q-mb-md"
          />
          
          <div class="broadcast-actions">
            <q-btn
              color="primary"
              label="Enviar Broadcast"
              @click="sendBroadcast"
              :loading="sendingBroadcast"
            />
            <q-btn
              flat
              color="grey"
              label="Cancelar"
              v-close-popup
              class="q-ml-sm"
            />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { chatbotService } from '../../services/chatbot'

export default {
  name: 'ChatbotAdmin',
  setup() {
    // Estado reativo
    const activeTab = ref('config')
    const refreshing = ref(false)
    const savingConfig = ref(false)
    const testingPrompt = ref(false)
    const loadingSessions = ref(false)
    const loadingLogs = ref(false)
    const sendingBroadcast = ref(false)
    
    // Modais
    const testPromptModal = ref(false)
    const broadcastModal = ref(false)
    
    // Status do bot
    const botStatus = reactive({
      online: true,
      lastCheck: null
    })
    
    // Configurações do bot
    const botConfig = reactive({
      bot_name: 'Bi UAI Bot Administrador',
      personality: 'amigável e profissional',
      system_prompt: '',
      model_name: 'llama3.2:3b',
      temperature: 0.7,
      max_tokens: 1000,
      enabled: true
    })
    
    // Analytics
    const analytics = reactive({
      total_sessions: 0,
      total_messages: 0,
      avg_session_duration: 0,
      most_common_questions: [],
      user_satisfaction: 0,
      response_time_avg: 0
    })
    
    // Sessões
    const sessions = ref([])
    const sessionsPagination = ref({
      page: 1,
      rowsPerPage: 10,
      rowsNumber: 0
    })
    
    // Base de conhecimento
    const selectedCategory = ref('funcionalidades')
    const knowledgeItems = ref([])
    
    // Teste de prompt
    const testMessage = ref('')
    const testResponse = ref('')
    
    // Broadcast
    const broadcastMessage = ref('')
    
    // Logs
    const logs = ref('')
    
    // Colunas da tabela de sessões
    const sessionsColumns = [
      {
        name: 'session_id',
        label: 'ID da Sessão',
        field: 'session_id',
        align: 'left'
      },
      {
        name: 'user_id',
        label: 'Usuário',
        field: 'user_id',
        align: 'left'
      },
      {
        name: 'messages_count',
        label: 'Mensagens',
        field: 'messages_count',
        align: 'center'
      },
      {
        name: 'created_at',
        label: 'Criado em',
        field: 'created_at',
        align: 'left',
        format: (val) => new Date(val).toLocaleString('pt-BR')
      },
      {
        name: 'status',
        label: 'Status',
        field: 'active',
        align: 'center'
      },
      {
        name: 'actions',
        label: 'Ações',
        field: 'actions',
        align: 'center'
      }
    ]
    
    // Categorias de conhecimento
    const knowledgeCategories = ref([
      {
        name: 'funcionalidades',
        label: 'Funcionalidades',
        icon: 'settings',
        count: 5
      },
      {
        name: 'navegacao',
        label: 'Navegação',
        icon: 'navigation',
        count: 3
      },
      {
        name: 'ajuda',
        label: 'Ajuda',
        icon: 'help',
        count: 7
      },
      {
        name: 'financeiro',
        label: 'Financeiro',
        icon: 'account_balance',
        count: 12
      }
    ])
    
    // Computadas
    const selectedCategoryLabel = computed(() => {
      const category = knowledgeCategories.value.find(c => c.name === selectedCategory.value)
      return category ? category.label : 'Todos'
    })
    
    // Métodos principais
    const refreshData = async () => {
      refreshing.value = true
      try {
        await Promise.all([
          loadBotStatus(),
          loadBotConfig(),
          loadAnalytics(),
          loadSessions()
        ])
        
        console.log('Dados atualizados com sucesso')
      } catch (error) {
        console.error('Erro ao atualizar dados:', error)
        console.error('Erro ao atualizar dados')
      } finally {
        refreshing.value = false
      }
    }
    
    const loadBotStatus = async () => {
      try {
        const health = await chatbotService.healthCheck()
        botStatus.online = health.status === 'healthy'
        botStatus.lastCheck = new Date().toISOString()
      } catch (error) {
        botStatus.online = false
      }
    }
    
    const loadBotConfig = async () => {
      try {
        const config = await chatbotService.getBotConfig()
        Object.assign(botConfig, config)
      } catch (error) {
        console.error('Erro ao carregar configuração:', error)
      }
    }
    
    const loadAnalytics = async () => {
      try {
        const data = await chatbotService.getAnalytics()
        Object.assign(analytics, data)
      } catch (error) {
        console.error('Erro ao carregar analytics:', error)
      }
    }
    
    const loadSessions = async () => {
      loadingSessions.value = true
      try {
        const data = await chatbotService.getAdminSessions(
          sessionsPagination.value.rowsPerPage,
          (sessionsPagination.value.page - 1) * sessionsPagination.value.rowsPerPage
        )
        
        sessions.value = data.sessions
        sessionsPagination.value.rowsNumber = data.total
      } catch (error) {
        console.error('Erro ao carregar sessões:', error)
      } finally {
        loadingSessions.value = false
      }
    }
    
    const saveConfig = async () => {
      savingConfig.value = true
      try {
        // Implementar salvamento de configuração
        console.log('Configurações salvas com sucesso')
      } catch (error) {
        console.error('Erro ao salvar configuração:', error)
        console.error('Erro ao salvar configurações')
      } finally {
        savingConfig.value = false
      }
    }
    
    const testPrompt = () => {
      testPromptModal.value = true
      testMessage.value = 'Como posso ver meus gastos deste mês?'
    }
    
    const runPromptTest = async () => {
      if (!testMessage.value.trim()) return
      
      testingPrompt.value = true
      try {
        const response = await chatbotService.sendMessage({
          message: testMessage.value,
          context: { test_mode: true }
        })
        
        testResponse.value = response.response
      } catch (error) {
        console.error('Erro no teste:', error)
        testResponse.value = 'Erro ao testar prompt'
      } finally {
        testingPrompt.value = false
      }
    }
    
    const resetConfig = () => {
      // Restaurar configuração padrão
      Object.assign(botConfig, {
        bot_name: 'Bi UAI Bot Administrador',
        personality: 'amigável e profissional',
        temperature: 0.7,
        max_tokens: 1000,
        enabled: true
      })
    }
    
    const resetPrompt = () => {
      botConfig.system_prompt = `Você é o Bi UAI Bot Administrador, um assistente especialista no sistema financeiro BIUAI.

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
- Sempre termine oferecendo mais ajuda`
    }
    
    const sendBroadcast = async () => {
      if (!broadcastMessage.value.trim()) return
      
      sendingBroadcast.value = true
      try {
        await chatbotService.sendBroadcast(broadcastMessage.value)
        
        console.log('Broadcast enviado com sucesso')
        
        broadcastModal.value = false
        broadcastMessage.value = ''
      } catch (error) {
        console.error('Erro ao enviar broadcast:', error)
        console.error('Erro ao enviar broadcast')
      } finally {
        sendingBroadcast.value = false
      }
    }
    
    const loadLogs = async () => {
      loadingLogs.value = true
      try {
        // Implementar carregamento de logs
        logs.value = 'Logs do sistema em desenvolvimento...'
      } catch (error) {
        console.error('Erro ao carregar logs:', error)
      } finally {
        loadingLogs.value = false
      }
    }
    
    // Eventos da tabela
    const onSessionsRequest = (props) => {
      sessionsPagination.value = props.pagination
      loadSessions()
    }
    
    const viewSession = (session) => {
      // Implementar visualização de sessão
      console.log('Visualização de sessão em desenvolvimento')
    }
    
    const deleteSession = (session) => {
      if (confirm('Deseja excluir a sessão ' + session.session_id + '?')) {
        // Implementar exclusão
        console.log('Sessão excluída')
      }
    }
    
    // Base de conhecimento
    const selectCategory = (category) => {
      selectedCategory.value = category.name
      loadKnowledgeItems()
    }
    
    const loadKnowledgeItems = () => {
      // Mock de itens de conhecimento
      knowledgeItems.value = [
        {
          id: 1,
          title: 'Como usar o Dashboard',
          content: 'O Dashboard oferece uma visão completa das suas finanças...'
        },
        {
          id: 2,
          title: 'Adicionar Lançamentos',
          content: 'Para adicionar um novo lançamento...'
        }
      ]
    }
    
    const addKnowledgeItem = () => {
      console.log('Adicionar item em desenvolvimento')
    }
    
    const editKnowledgeItem = (item) => {
      console.log('Editar item em desenvolvimento')
    }
    
    const deleteKnowledgeItem = (item) => {
      if (confirm('Deseja excluir o item "' + item.title + '"?')) {
        console.log('Item excluído')
      }
    }
    
    // Ciclo de vida
    onMounted(() => {
      refreshData()
      resetPrompt()
      loadKnowledgeItems()
    })
    
    return {
      // Estado
      activeTab,
      refreshing,
      savingConfig,
      testingPrompt,
      loadingSessions,
      loadingLogs,
      sendingBroadcast,
      testPromptModal,
      broadcastModal,
      botStatus,
      botConfig,
      analytics,
      sessions,
      sessionsPagination,
      sessionsColumns,
      selectedCategory,
      knowledgeItems,
      knowledgeCategories,
      testMessage,
      testResponse,
      broadcastMessage,
      logs,
      
      // Computadas
      selectedCategoryLabel,
      
      // Métodos
      refreshData,
      saveConfig,
      testPrompt,
      runPromptTest,
      resetConfig,
      resetPrompt,
      sendBroadcast,
      loadLogs,
      onSessionsRequest,
      viewSession,
      deleteSession,
      selectCategory,
      addKnowledgeItem,
      editKnowledgeItem,
      deleteKnowledgeItem,
      loadSessions
    }
  }
}
</script>

<style lang="scss" scoped>
.chatbot-admin-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
  
  .page-title {
    margin: 0 0 8px 0;
    color: #1976d2;
  }
  
  .page-subtitle {
    margin: 0;
    color: #666;
    font-size: 14px;
  }
}

.status-cards {
  margin-bottom: 24px;
  
  .status-card {
    height: 100%;
    
    .status-content {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    
    .status-text {
      .status-label {
        font-size: 12px;
        color: #666;
        margin-bottom: 4px;
      }
      
      .status-value {
        font-size: 20px;
        font-weight: 600;
        color: #333;
      }
    }
  }
}

.admin-tabs {
  margin-bottom: 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.admin-panels {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-height: 500px;
}

.config-card,
.analytics-card,
.sessions-card,
.knowledge-card,
.logs-card {
  height: 100%;
  
  h6 {
    margin: 0 0 16px 0;
    color: #333;
  }
}

.config-actions,
.prompt-actions,
.broadcast-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.metrics-list {
  .metric-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
    
    .metric-label {
      color: #666;
    }
    
    .metric-value {
      font-weight: 600;
      color: #333;
    }
  }
}

.chart-placeholder {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 16px 0;
}

.item-actions {
  display: flex;
  gap: 4px;
}

.logs-content {
  max-height: 400px;
  overflow-y: auto;
  
  .logs-text {
    font-family: 'Courier New', monospace;
    font-size: 12px;
    white-space: pre-wrap;
    margin: 0;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 4px;
  }
}

.test-response {
  margin-top: 16px;
  
  h6 {
    margin-bottom: 8px;
  }
  
  .response-content {
    padding: 12px;
    background: #f8f9fa;
    border-radius: 4px;
    border-left: 4px solid #1976d2;
  }
}

// Responsividade
@media (max-width: 768px) {
  .chatbot-admin-page {
    padding: 16px;
  }
  
  .status-cards .row {
    flex-direction: column;
  }
  
  .config-section .row {
    flex-direction: column;
  }
  
  .analytics-section .row {
    flex-direction: column;
  }
}
</style> 