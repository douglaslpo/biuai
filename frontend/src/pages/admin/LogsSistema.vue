<template>
  <v-container fluid class="pa-6">
    <div class="d-flex align-center mb-6">
      <v-icon color="primary" size="32" class="mr-3">mdi-math-log</v-icon>
      <div>
        <h1 class="text-h4 font-weight-bold">Logs do Sistema</h1>
        <p class="text-subtitle-1 text-medium-emphasis mb-0">
          Monitoramento e análise dos logs de aplicação
        </p>
      </div>
    </div>

    <v-row>
      <!-- Filtros e Controles -->
      <v-col cols="12" md="3">
        <BaseCard title="Filtros" icon="mdi-filter">
          <v-select
            v-model="filters.level"
            label="Nível do Log"
            :items="logLevels"
            variant="outlined"
            clearable
            class="mb-3"
          />
          
          <v-select
            v-model="filters.service"
            label="Serviço"
            :items="services"
            variant="outlined"
            clearable
            class="mb-3"
          />
          
          <v-text-field
            v-model="filters.search"
            label="Buscar"
            placeholder="Buscar nos logs..."
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            clearable
            class="mb-3"
          />
          
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="filters.dateFrom"
                label="Data Início"
                type="datetime-local"
                variant="outlined"
                class="mb-3"
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="filters.dateTo"
                label="Data Fim"
                type="datetime-local"
                variant="outlined"
                class="mb-3"
              />
            </v-col>
          </v-row>
          
          <v-btn
            color="primary"
            variant="elevated"
            @click="applyFilters"
            block
            class="mb-2"
          >
            <v-icon start>mdi-filter-check</v-icon>
            Aplicar Filtros
          </v-btn>
          
          <v-btn
            variant="outlined"
            @click="clearFilters"
            block
          >
            <v-icon start>mdi-filter-remove</v-icon>
            Limpar Filtros
          </v-btn>
        </BaseCard>

        <!-- Estatísticas -->
        <BaseCard title="Estatísticas" icon="mdi-chart-pie" class="mt-4">
          <v-list density="compact">
            <v-list-item
              v-for="stat in logStats"
              :key="stat.level"
              :prepend-icon="getLevelIcon(stat.level)"
              :title="stat.level.toUpperCase()"
              :subtitle="stat.count.toString()"
              :class="getLevelColor(stat.level)"
            />
          </v-list>
        </BaseCard>

        <!-- Controles -->
        <BaseCard title="Controles" icon="mdi-cog" class="mt-4">
          <div class="d-flex flex-column gap-2">
            <v-btn
              color="success"
              variant="outlined"
              size="small"
              @click="downloadLogs"
            >
              <v-icon start>mdi-download</v-icon>
              Exportar Logs
            </v-btn>
            
            <v-btn
              color="warning"
              variant="outlined"
              size="small"
              @click="clearLogs"
            >
              <v-icon start>mdi-delete-sweep</v-icon>
              Limpar Logs
            </v-btn>
            
            <v-btn
              color="info"
              variant="outlined"
              size="small"
              @click="refreshLogs"
            >
              <v-icon start>mdi-refresh</v-icon>
              Atualizar
            </v-btn>
          </div>
          
          <v-switch
            v-model="autoRefresh"
            label="Auto-refresh"
            color="primary"
            inset
            class="mt-3"
          />
        </BaseCard>
      </v-col>

      <!-- Lista de Logs -->
      <v-col cols="12" md="9">
        <BaseCard title="Logs em Tempo Real" icon="mdi-console">
          <template #actions>
            <v-chip
              :color="isConnected ? 'success' : 'error'"
              size="small"
              variant="elevated"
            >
              <v-icon start>{{ isConnected ? 'mdi-wifi' : 'mdi-wifi-off' }}</v-icon>
              {{ isConnected ? 'Conectado' : 'Desconectado' }}
            </v-chip>
          </template>
          
          <!-- Controles da visualização -->
          <div class="d-flex justify-space-between align-center mb-4">
            <div class="d-flex align-center gap-3">
              <v-btn-toggle
                v-model="viewMode"
                mandatory
                variant="outlined"
                density="compact"
              >
                <v-btn value="table">
                  <v-icon>mdi-table</v-icon>
                </v-btn>
                <v-btn value="console">
                  <v-icon>mdi-console</v-icon>
                </v-btn>
              </v-btn-toggle>
              
              <v-select
                v-model="pageSize"
                :items="[25, 50, 100, 200]"
                label="Por página"
                variant="outlined"
                density="compact"
                style="width: 120px;"
              />
            </div>
            
            <div class="text-caption text-medium-emphasis">
              {{ filteredLogs.length }} logs encontrados
            </div>
          </div>
          
          <!-- Visualização em Tabela -->
          <div v-if="viewMode === 'table'">
            <v-data-table
              :headers="logHeaders"
              :items="paginatedLogs"
              :loading="loading"
              item-value="id"
              class="elevation-1"
              density="compact"
              @click:row="selectLog"
            >
              <template v-slot:item.level="{ item }">
                <v-chip
                  :color="getLevelColor(item.level)"
                  size="small"
                  variant="elevated"
                >
                  <v-icon start>{{ getLevelIcon(item.level) }}</v-icon>
                  {{ item.level.toUpperCase() }}
                </v-chip>
              </template>
              
              <template v-slot:item.timestamp="{ item }">
                {{ formatTimestamp(item.timestamp) }}
              </template>
              
              <template v-slot:item.message="{ item }">
                <div class="log-message">
                  {{ truncateMessage(item.message) }}
                </div>
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  color="primary"
                  variant="text"
                  size="small"
                  @click.stop="selectLog(item)"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
              </template>
            </v-data-table>
            
            <!-- Paginação -->
            <div class="d-flex justify-center mt-4">
              <v-pagination
                v-model="currentPage"
                :length="totalPages"
                :total-visible="7"
              />
            </div>
          </div>
          
          <!-- Visualização em Console -->
          <div v-else class="console-view">
            <div
              ref="consoleContainer"
              class="console-container"
            >
              <div
                v-for="log in paginatedLogs"
                :key="log.id"
                :class="['log-line', `log-${log.level}`]"
                @click="selectLog(log)"
              >
                <span class="log-timestamp">{{ formatTimestamp(log.timestamp) }}</span>
                <span :class="['log-level', `level-${log.level}`]">[{{ log.level.toUpperCase() }}]</span>
                <span class="log-service">[{{ log.service }}]</span>
                <span class="log-message">{{ log.message }}</span>
              </div>
            </div>
          </div>
        </BaseCard>
      </v-col>
    </v-row>

    <!-- Dialog de Detalhes do Log -->
    <v-dialog v-model="showLogDialog" max-width="800">
      <BaseCard v-if="selectedLog" title="Detalhes do Log" icon="mdi-text-box">
        <v-row>
          <v-col cols="12" md="6">
            <v-list density="compact">
              <v-list-item
                prepend-icon="mdi-clock"
                title="Timestamp"
                :subtitle="formatTimestamp(selectedLog.timestamp)"
              />
              <v-list-item
                prepend-icon="mdi-tag"
                title="Nível"
                :subtitle="selectedLog.level.toUpperCase()"
              />
              <v-list-item
                prepend-icon="mdi-server"
                title="Serviço"
                :subtitle="selectedLog.service"
              />
              <v-list-item
                v-if="selectedLog.user_id"
                prepend-icon="mdi-account"
                title="Usuário"
                :subtitle="selectedLog.user_id"
              />
            </v-list>
          </v-col>
          <v-col cols="12" md="6">
            <v-list density="compact">
              <v-list-item
                v-if="selectedLog.ip_address"
                prepend-icon="mdi-ip"
                title="IP Address"
                :subtitle="selectedLog.ip_address"
              />
              <v-list-item
                v-if="selectedLog.request_id"
                prepend-icon="mdi-identifier"
                title="Request ID"
                :subtitle="selectedLog.request_id"
              />
              <v-list-item
                v-if="selectedLog.file"
                prepend-icon="mdi-file"
                title="Arquivo"
                :subtitle="selectedLog.file"
              />
              <v-list-item
                v-if="selectedLog.line"
                prepend-icon="mdi-numeric"
                title="Linha"
                :subtitle="selectedLog.line"
              />
            </v-list>
          </v-col>
        </v-row>
        
        <v-divider class="my-4" />
        
        <h3 class="text-h6 mb-3">Mensagem</h3>
        <v-card variant="outlined" class="mb-4">
          <v-card-text>
            <pre class="log-content">{{ selectedLog.message }}</pre>
          </v-card-text>
        </v-card>
        
        <div v-if="selectedLog.stack_trace">
          <h3 class="text-h6 mb-3">Stack Trace</h3>
          <v-card variant="outlined">
            <v-card-text>
              <pre class="log-content">{{ selectedLog.stack_trace }}</pre>
            </v-card-text>
          </v-card>
        </div>
        
        <template #actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="showLogDialog = false"
          >
            Fechar
          </v-btn>
          <v-btn
            color="primary"
            @click="copyLogDetails"
          >
            Copiar
          </v-btn>
        </template>
      </BaseCard>
    </v-dialog>

    <!-- Snackbar -->
    <v-snackbar
      v-model="showNotification"
      :color="notificationType"
      timeout="5000"
    >
      {{ notificationMessage }}
      <template v-slot:actions>
        <v-btn
          color="white"
          variant="text"
          @click="showNotification = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import BaseCard from '@/components/base/BaseCard.vue'
import { api } from '@/boot/axios'

// Estado reativo
const loading = ref(false)
const isConnected = ref(false)
const autoRefresh = ref(false)
const viewMode = ref('table')
const pageSize = ref(50)
const currentPage = ref(1)
const showLogDialog = ref(false)
const selectedLog = ref(null)
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref('info')

// Filtros
const filters = reactive({
  level: null,
  service: null,
  search: '',
  dateFrom: '',
  dateTo: ''
})

// Dados
const logs = ref([])
const logStats = ref([
  { level: 'error', count: 12 },
  { level: 'warning', count: 45 },
  { level: 'info', count: 234 },
  { level: 'debug', count: 567 }
])

// Opções
const logLevels = [
  { title: 'ERROR', value: 'error' },
  { title: 'WARNING', value: 'warning' },
  { title: 'INFO', value: 'info' },
  { title: 'DEBUG', value: 'debug' }
]

const services = [
  { title: 'Backend', value: 'backend' },
  { title: 'Frontend', value: 'frontend' },
  { title: 'Database', value: 'database' },
  { title: 'Redis', value: 'redis' },
  { title: 'Model Server', value: 'model-server' }
]

// Headers da tabela
const logHeaders = [
  { title: 'Timestamp', key: 'timestamp', sortable: true },
  { title: 'Nível', key: 'level', sortable: true },
  { title: 'Serviço', key: 'service', sortable: true },
  { title: 'Mensagem', key: 'message', sortable: false },
  { title: 'Ações', key: 'actions', sortable: false }
]

// Computed
const filteredLogs = computed(() => {
  let filtered = logs.value

  if (filters.level) {
    filtered = filtered.filter(log => log.level === filters.level)
  }

  if (filters.service) {
    filtered = filtered.filter(log => log.service === filters.service)
  }

  if (filters.search) {
    const search = filters.search.toLowerCase()
    filtered = filtered.filter(log => 
      log.message.toLowerCase().includes(search) ||
      log.service.toLowerCase().includes(search)
    )
  }

  if (filters.dateFrom) {
    const fromDate = new Date(filters.dateFrom)
    filtered = filtered.filter(log => new Date(log.timestamp) >= fromDate)
  }

  if (filters.dateTo) {
    const toDate = new Date(filters.dateTo)
    filtered = filtered.filter(log => new Date(log.timestamp) <= toDate)
  }

  return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

const totalPages = computed(() => {
  return Math.ceil(filteredLogs.value.length / pageSize.value)
})

const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredLogs.value.slice(start, end)
})

// Métodos
const loadLogs = async () => {
  loading.value = true
  
  try {
    const response = await api.get('/admin/logs', {
      params: {
        limit: 1000,
        ...filters
      }
    })
    
    logs.value = response.data.logs || []
    logStats.value = response.data.stats || logStats.value
    
  } catch (error) {
    showNotificationMessage('Erro ao carregar logs: ' + error.message, 'error')
    
    // Dados mock para demonstração
    logs.value = generateMockLogs()
  } finally {
    loading.value = false
  }
}

const generateMockLogs = () => {
  const mockLogs = []
  const levels = ['error', 'warning', 'info', 'debug']
  const services = ['backend', 'frontend', 'database', 'redis']
  const messages = [
    'User login successful',
    'Database connection established',
    'Failed to process request',
    'Memory usage at 85%',
    'Cache miss for key: user_123',
    'API request completed in 250ms',
    'Backup process started',
    'Error connecting to external service',
    'New user registered',
    'Session expired for user'
  ]

  for (let i = 0; i < 100; i++) {
    const timestamp = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000)
    mockLogs.push({
      id: i + 1,
      timestamp: timestamp.toISOString(),
      level: levels[Math.floor(Math.random() * levels.length)],
      service: services[Math.floor(Math.random() * services.length)],
      message: messages[Math.floor(Math.random() * messages.length)],
      user_id: Math.random() > 0.7 ? Math.floor(Math.random() * 100) : null,
      ip_address: `192.168.1.${Math.floor(Math.random() * 255)}`,
      request_id: `req_${Math.random().toString(36).substr(2, 9)}`
    })
  }

  return mockLogs
}

const applyFilters = () => {
  currentPage.value = 1
  loadLogs()
}

const clearFilters = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = ''
  })
  filters.level = null
  filters.service = null
  currentPage.value = 1
  loadLogs()
}

const selectLog = (log) => {
  selectedLog.value = log
  showLogDialog.value = true
}

const refreshLogs = () => {
  loadLogs()
  showNotificationMessage('Logs atualizados!', 'info')
}

const downloadLogs = () => {
  const dataStr = JSON.stringify(filteredLogs.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `logs_${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  showNotificationMessage('Logs exportados com sucesso!', 'success')
}

const clearLogs = async () => {
  if (!confirm('Tem certeza que deseja limpar todos os logs? Esta ação não pode ser desfeita.')) {
    return
  }
  
  try {
    await api.delete('/admin/logs')
    logs.value = []
    showNotificationMessage('Logs limpos com sucesso!', 'success')
  } catch (error) {
    showNotificationMessage('Erro ao limpar logs: ' + error.message, 'error')
  }
}

const copyLogDetails = () => {
  if (!selectedLog.value) return
  
  const details = JSON.stringify(selectedLog.value, null, 2)
  navigator.clipboard.writeText(details).then(() => {
    showNotificationMessage('Detalhes copiados!', 'success')
  })
}

// Utilitários
const getLevelIcon = (level) => {
  const icons = {
    error: 'mdi-alert-circle',
    warning: 'mdi-alert',
    info: 'mdi-information',
    debug: 'mdi-bug'
  }
  return icons[level] || 'mdi-circle'
}

const getLevelColor = (level) => {
  const colors = {
    error: 'error',
    warning: 'warning',
    info: 'info',
    debug: 'default'
  }
  return colors[level] || 'default'
}

const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleString('pt-BR')
}

const truncateMessage = (message, length = 100) => {
  return message.length > length ? message.substring(0, length) + '...' : message
}

const showNotificationMessage = (message, type = 'info') => {
  notificationMessage.value = message
  notificationType.value = type
  showNotification.value = true
}

// Auto-refresh
let refreshInterval = null

const startAutoRefresh = () => {
  if (refreshInterval) clearInterval(refreshInterval)
  refreshInterval = setInterval(() => {
    if (autoRefresh.value) {
      loadLogs()
    }
  }, 10000) // 10 segundos
}

const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

// Lifecycle
onMounted(() => {
  loadLogs()
  startAutoRefresh()
  isConnected.value = true
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style lang="scss" scoped>
.console-view {
  .console-container {
    background: #1e1e1e;
    color: #ffffff;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    padding: 16px;
    border-radius: 8px;
    height: 600px;
    overflow-y: auto;
  }

  .log-line {
    padding: 2px 0;
    cursor: pointer;
    border-radius: 2px;
    
    &:hover {
      background: rgba(255, 255, 255, 0.1);
    }
  }

  .log-timestamp {
    color: #888;
    margin-right: 8px;
  }

  .log-level {
    margin-right: 8px;
    font-weight: bold;
    
    &.level-error { color: #ff5252; }
    &.level-warning { color: #ff9800; }
    &.level-info { color: #2196f3; }
    &.level-debug { color: #9e9e9e; }
  }

  .log-service {
    color: #4caf50;
    margin-right: 8px;
  }

  .log-message {
    color: #ffffff;
  }
}

.log-message {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.log-content {
  background: rgb(var(--v-theme-surface-variant));
  padding: 16px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.v-data-table {
  border-radius: 8px;
  overflow: hidden;
}
</style> 