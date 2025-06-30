<template>
  <v-container fluid class="pa-6">
    <div class="d-flex align-center mb-6">
      <v-icon color="primary" size="32" class="mr-3">mdi-api</v-icon>
      <div>
        <h1 class="text-h4 font-weight-bold">Documentação da API</h1>
        <p class="text-subtitle-1 text-medium-emphasis mb-0">
          Explore e teste os endpoints da API BIUAI
        </p>
      </div>
    </div>

    <v-row>
      <!-- Informações da API -->
      <v-col cols="12" md="4">
        <BaseCard title="Informações da API" icon="mdi-information">
          <v-list density="compact">
            <v-list-item
              prepend-icon="mdi-server"
              title="Servidor"
              :subtitle="apiInfo.server"
            />
            <v-list-item
              prepend-icon="mdi-tag"
              title="Versão"
              :subtitle="apiInfo.version"
            />
            <v-list-item
              prepend-icon="mdi-shield-check"
              title="Autenticação"
              :subtitle="apiInfo.auth"
            />
            <v-list-item
              prepend-icon="mdi-clock"
              title="Rate Limit"
              :subtitle="apiInfo.rateLimit"
            />
          </v-list>
        </BaseCard>

        <!-- Links Úteis -->
        <BaseCard title="Links Úteis" icon="mdi-link" class="mt-4">
          <div class="d-flex flex-column gap-2">
            <v-btn
              variant="outlined"
              color="primary"
              @click="openSwagger"
            >
              <v-icon start>mdi-api</v-icon>
              Swagger UI
            </v-btn>
            
            <v-btn
              variant="outlined"
              color="success"
              @click="openRedoc"
            >
              <v-icon start>mdi-file-document</v-icon>
              ReDoc
            </v-btn>
            
            <v-btn
              variant="outlined"
              color="info"
              @click="downloadOpenAPI"
            >
              <v-icon start>mdi-download</v-icon>
              OpenAPI Spec
            </v-btn>
            
            <v-btn
              variant="outlined"
              color="warning"
              @click="openPostman"
            >
              <v-icon start>mdi-application-export</v-icon>
              Collection Postman
            </v-btn>
          </div>
        </BaseCard>

        <!-- Estatísticas -->
        <BaseCard title="Estatísticas da API" icon="mdi-chart-bar" class="mt-4">
          <v-list density="compact">
            <v-list-item
              v-for="stat in apiStats"
              :key="stat.label"
              :prepend-icon="stat.icon"
              :title="stat.label"
              :subtitle="stat.value"
            />
          </v-list>
        </BaseCard>
      </v-col>

      <!-- Swagger UI Embarcado -->
      <v-col cols="12" md="8">
        <BaseCard title="Documentação Interativa" icon="mdi-api">
          <div class="d-flex justify-space-between align-center mb-4">
            <v-chip-group v-model="selectedEnvironment" mandatory>
              <v-chip
                v-for="env in environments"
                :key="env.value"
                :value="env.value"
                color="primary"
                variant="outlined"
              >
                {{ env.title }}
              </v-chip>
            </v-chip-group>
          </div>
          
          <!-- Documentações Disponíveis -->
          <div class="docs-grid">
            <v-card
              variant="outlined"
              class="docs-card"
              @click="openSwagger"
            >
              <v-card-text class="text-center pa-6">
                <v-icon color="primary" size="48" class="mb-3">mdi-api</v-icon>
                <h3 class="text-h6 mb-2">Swagger UI</h3>
                <p class="text-body-2 text-medium-emphasis mb-3">
                  Interface interativa para testar todos os endpoints da API
                </p>
                <v-btn
                  color="primary"
                  variant="elevated"
                  @click="openSwagger"
                  block
                >
                  <v-icon start>mdi-api</v-icon>
                  Abrir Swagger UI
                </v-btn>
              </v-card-text>
            </v-card>

            <v-card
              variant="outlined"
              class="docs-card"
              @click="openRedoc"
            >
              <v-card-text class="text-center pa-6">
                <v-icon color="secondary" size="48" class="mb-3">mdi-file-document</v-icon>
                <h3 class="text-h6 mb-2">ReDoc</h3>
                <p class="text-body-2 text-medium-emphasis mb-3">
                  Documentação detalhada e organizada da API
                </p>
                <v-btn
                  color="secondary"
                  variant="outlined"
                  @click="openRedoc"
                  block
                >
                  <v-icon start>mdi-file-document</v-icon>
                  Abrir ReDoc
                </v-btn>
              </v-card-text>
            </v-card>
          </div>

          <!-- Ações Rápidas -->
          <v-divider class="my-6" />
          
          <div class="d-flex flex-wrap gap-3">
            <v-btn
              variant="outlined"
              color="info"
              @click="downloadOpenAPI"
            >
              <v-icon start>mdi-download</v-icon>
              Baixar OpenAPI Spec
            </v-btn>
            
            <v-btn
              variant="outlined"
              color="warning"
              @click="openPostman"
            >
              <v-icon start>mdi-application-export</v-icon>
              Collection Postman
            </v-btn>

            <v-btn
              variant="outlined"
              color="purple"
              @click="copyApiUrl"
            >
              <v-icon start>mdi-content-copy</v-icon>
              Copiar URL da API
            </v-btn>
          </div>

          <!-- Status da API -->
          <v-alert
            type="success"
            variant="tonal"
            class="mt-4"
          >
            <v-icon start>mdi-check-circle</v-icon>
            API está online e funcionando normalmente
          </v-alert>
        </BaseCard>
      </v-col>

      <!-- Endpoints Rápidos -->
      <v-col cols="12">
        <BaseCard title="Endpoints Principais" icon="mdi-routes">
          <v-expansion-panels variant="accordion">
            <v-expansion-panel
              v-for="group in endpointGroups"
              :key="group.name"
              :title="group.name"
              :text="group.description"
            >
              <template v-slot:text>
                <v-list density="compact">
                  <v-list-item
                    v-for="endpoint in group.endpoints"
                    :key="endpoint.path"
                    class="mb-2"
                  >
                    <template v-slot:prepend>
                      <v-chip
                        :color="getMethodColor(endpoint.method)"
                        size="small"
                        variant="elevated"
                        class="mr-3"
                      >
                        {{ endpoint.method }}
                      </v-chip>
                    </template>
                    
                    <v-list-item-title>{{ endpoint.path }}</v-list-item-title>
                    <v-list-item-subtitle>{{ endpoint.description }}</v-list-item-subtitle>
                    
                    <template v-slot:append>
                      <v-btn
                        color="primary"
                        variant="text"
                        size="small"
                        @click="testEndpoint(endpoint)"
                      >
                        Testar
                      </v-btn>
                    </template>
                  </v-list-item>
                </v-list>
              </template>
            </v-expansion-panel>
          </v-expansion-panels>
        </BaseCard>
      </v-col>
    </v-row>

    <!-- Dialog de Teste de Endpoint -->
    <v-dialog v-model="showTestDialog" max-width="800">
      <BaseCard :title="`Testar ${selectedEndpoint?.method} ${selectedEndpoint?.path}`" icon="mdi-test-tube">
        <v-form @submit.prevent="executeTest">
          <!-- Headers -->
          <h3 class="text-h6 mb-3">Headers</h3>
          <v-textarea
            v-model="testRequest.headers"
            label="Headers (JSON)"
            placeholder='{"Authorization": "Bearer token", "Content-Type": "application/json"}'
            variant="outlined"
            rows="3"
            class="mb-4"
          />
          
          <!-- Body (para POST/PUT) -->
          <div v-if="['POST', 'PUT', 'PATCH'].includes(selectedEndpoint?.method)">
            <h3 class="text-h6 mb-3">Body</h3>
            <v-textarea
              v-model="testRequest.body"
              label="Request Body (JSON)"
              placeholder='{"key": "value"}'
              variant="outlined"
              rows="5"
              class="mb-4"
            />
          </div>
          
          <!-- Resposta -->
          <div v-if="testResponse">
            <h3 class="text-h6 mb-3">Resposta</h3>
            <v-card variant="outlined" class="mb-4">
              <v-card-text>
                <div class="d-flex align-center mb-2">
                  <v-chip
                    :color="testResponse.status >= 200 && testResponse.status < 300 ? 'success' : 'error'"
                    size="small"
                  >
                    {{ testResponse.status }}
                  </v-chip>
                  <span class="ml-2 text-caption">{{ testResponse.statusText }}</span>
                </div>
                <pre class="response-body">{{ JSON.stringify(testResponse.data, null, 2) }}</pre>
              </v-card-text>
            </v-card>
          </div>
          
          <template #actions>
            <v-spacer />
            <v-btn
              variant="text"
              @click="showTestDialog = false"
            >
              Fechar
            </v-btn>
            <v-btn
              type="submit"
              color="primary"
              :loading="testing"
            >
              Executar Teste
            </v-btn>
          </template>
        </v-form>
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
import { ref, reactive, computed, onMounted } from 'vue'
import BaseCard from '@/components/base/BaseCard.vue'
import { api } from '@/boot/axios'

// Estado reativo
const selectedEnvironment = ref('development')
const showTestDialog = ref(false)
const selectedEndpoint = ref(null)
const testing = ref(false)
const testResponse = ref(null)
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref('info')

// Informações da API
const apiInfo = ref({
  server: 'http://localhost:3000',
  version: '2.0.0',
  auth: 'JWT Bearer Token',
  rateLimit: '100 req/min'
})

// Ambientes
const environments = [
  { title: 'Desenvolvimento', value: 'development' },
  { title: 'Homologação', value: 'staging' },
  { title: 'Produção', value: 'production' }
]

// Estatísticas da API
const apiStats = ref([
  { label: 'Total de Endpoints', value: '42', icon: 'mdi-api' },
  { label: 'Endpoints Públicos', value: '8', icon: 'mdi-earth' },
  { label: 'Endpoints Protegidos', value: '34', icon: 'mdi-shield-lock' },
  { label: 'Uptime', value: '99.9%', icon: 'mdi-server' }
])

// Grupos de endpoints
const endpointGroups = ref([
  {
    name: 'Autenticação',
    description: 'Endpoints para login, registro e gerenciamento de tokens',
    endpoints: [
      { method: 'POST', path: '/api/v1/auth/login', description: 'Fazer login no sistema' },
      { method: 'POST', path: '/api/v1/auth/register', description: 'Registrar novo usuário' },
      { method: 'GET', path: '/api/v1/auth/me', description: 'Obter dados do usuário atual' },
      { method: 'POST', path: '/api/v1/auth/refresh', description: 'Renovar token de acesso' }
    ]
  },
  {
    name: 'Financeiro',
    description: 'Gerenciamento de lançamentos financeiros',
    endpoints: [
      { method: 'GET', path: '/api/v1/financeiro', description: 'Listar lançamentos' },
      { method: 'POST', path: '/api/v1/financeiro', description: 'Criar novo lançamento' },
      { method: 'PUT', path: '/api/v1/financeiro/{id}', description: 'Atualizar lançamento' },
      { method: 'DELETE', path: '/api/v1/financeiro/{id}', description: 'Excluir lançamento' }
    ]
  },
  {
    name: 'Relatórios',
    description: 'Geração de relatórios e análises',
    endpoints: [
      { method: 'GET', path: '/api/v1/financeiro/summary', description: 'Resumo financeiro' },
      { method: 'GET', path: '/api/v1/financeiro/analytics', description: 'Análises financeiras' },
      { method: 'POST', path: '/api/v1/reports/generate', description: 'Gerar relatório customizado' }
    ]
  },
  {
    name: 'Administração',
    description: 'Endpoints administrativos do sistema',
    endpoints: [
      { method: 'GET', path: '/api/v1/admin/users', description: 'Listar usuários' },
      { method: 'POST', path: '/api/v1/admin/backup', description: 'Criar backup' },
      { method: 'GET', path: '/api/v1/admin/logs', description: 'Visualizar logs' },
      { method: 'GET', path: '/api/v1/admin/health', description: 'Status do sistema' }
    ]
  }
])

// Formulário de teste
const testRequest = reactive({
  headers: '{"Authorization": "Bearer your-token-here"}',
  body: ''
})

// URLs computadas
const swaggerUrl = computed(() => {
  const baseUrls = {
    development: 'http://localhost:3000/docs',
    staging: 'https://staging-api.biuai.com/docs',
    production: 'https://api.biuai.com/docs'
  }
  return baseUrls[selectedEnvironment.value]
})

// Métodos
const openSwagger = () => {
  window.open(swaggerUrl.value, '_blank')
}

const openRedoc = () => {
  const redocUrls = {
    development: 'http://localhost:3000/redoc',
    staging: 'https://staging-api.biuai.com/redoc',
    production: 'https://api.biuai.com/redoc'
  }
  window.open(redocUrls[selectedEnvironment.value], '_blank')
}

const downloadOpenAPI = () => {
  const link = document.createElement('a')
  link.href = `${apiInfo.value.server}/api/v1/openapi.json`
  link.download = 'biuai-openapi.json'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  showNotificationMessage('Especificação OpenAPI baixada!', 'success')
}

const openPostman = () => {
  const link = document.createElement('a')
  link.href = `${apiInfo.value.server}/postman-collection.json`
  link.download = 'biuai-postman-collection.json'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  showNotificationMessage('Collection do Postman baixada!', 'success')
}

const copyApiUrl = () => {
  const url = apiInfo.value.server
  navigator.clipboard.writeText(url)
  showNotificationMessage('URL da API copiada para o clipboard!', 'success')
}

const testEndpoint = (endpoint) => {
  selectedEndpoint.value = endpoint
  testResponse.value = null
  
  // Pré-popular body para métodos que precisam
  if (['POST', 'PUT', 'PATCH'].includes(endpoint.method)) {
    if (endpoint.path.includes('financeiro')) {
      testRequest.body = JSON.stringify({
        descricao: "Teste via API Docs",
        valor: 100.00,
        tipo: "receita",
        categoria: "Teste",
        data_lancamento: new Date().toISOString().split('T')[0]
      }, null, 2)
    } else if (endpoint.path.includes('auth/login')) {
      testRequest.body = JSON.stringify({
        username: "demo@biuai.com",
        password: "demo123"
      }, null, 2)
    } else {
      testRequest.body = '{}'
    }
  }
  
  showTestDialog.value = true
}

const executeTest = async () => {
  if (!selectedEndpoint.value) return
  
  testing.value = true
  
  try {
    let headers = {}
    let body = null
    
    // Parse headers
    if (testRequest.headers) {
      headers = JSON.parse(testRequest.headers)
    }
    
    // Parse body para métodos que precisam
    if (['POST', 'PUT', 'PATCH'].includes(selectedEndpoint.value.method) && testRequest.body) {
      body = JSON.parse(testRequest.body)
    }
    
    // Fazer requisição
    const config = {
      method: selectedEndpoint.value.method.toLowerCase(),
      url: selectedEndpoint.value.path,
      headers,
      ...(body && { data: body })
    }
    
    const response = await api(config)
    
    testResponse.value = {
      status: response.status,
      statusText: response.statusText,
      data: response.data
    }
    
    showNotificationMessage('Teste executado com sucesso!', 'success')
  } catch (error) {
    testResponse.value = {
      status: error.response?.status || 500,
      statusText: error.response?.statusText || 'Error',
      data: error.response?.data || { error: error.message }
    }
    
    showNotificationMessage('Erro no teste: ' + error.message, 'error')
  } finally {
    testing.value = false
  }
}

const getMethodColor = (method) => {
  const colors = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    PATCH: 'info',
    DELETE: 'error'
  }
  return colors[method] || 'default'
}

const showNotificationMessage = (message, type = 'info') => {
  notificationMessage.value = message
  notificationType.value = type
  showNotification.value = true
}

// Lifecycle
onMounted(() => {
  // Carregar informações da API
  api.get('/health').then(response => {
    if (response.data.version) {
      apiInfo.value.version = response.data.version
    }
  }).catch(() => {
    // Ignorar erro se endpoint não existir
  })
})
</script>

<style lang="scss" scoped>
.swagger-container {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
  overflow: hidden;
}

.swagger-iframe {
  border-radius: 8px;
}

.response-body {
  background: rgb(var(--v-theme-surface-variant));
  padding: 16px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.v-expansion-panel-text {
  padding: 16px;
}

.docs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.docs-card {
  border: 2px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.docs-card:hover {
  border-color: rgba(var(--v-theme-primary), 0.5);
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.docs-card-text {
  padding: 16px;
}
</style> 