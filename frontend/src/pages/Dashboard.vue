<template>
  <div class="biuai-dashboard">
    <!-- Header simplificado -->
    <v-app-bar 
      color="transparent" 
      elevation="0" 
      height="80"
      class="dashboard-header"
    >
      <v-container class="d-flex align-center justify-space-between">
        <div class="header-info">
          <h1 class="text-h4 font-weight-bold text-primary">
            Dashboard BIUAI
          </h1>
          <p class="text-subtitle-1 text-medium-emphasis mb-0">
            Bem-vindo, {{ authStore.user?.nome || 'Usuário' }}
          </p>
        </div>
        
        <div class="header-actions d-flex align-center ga-3">
          <v-btn
            icon="mdi-refresh"
            variant="text"
            @click="refreshAllData"
            :loading="loading"
            size="large"
          />
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="showNewLancamento = true"
            variant="elevated"
          >
            Novo Lançamento
          </v-btn>
        </div>
      </v-container>
    </v-app-bar>

    <!-- Cards de Métricas -->
    <v-container class="py-6">
      <MetricsGrid 
        :summary="summary"
        :loading="loading"
        :trend-data="trendData"
        @action="handleMetricAction"
        class="mb-8"
      />

      <!-- Insights e Alertas Modernos -->
      <v-row v-if="insights.length > 0 || alerts.length > 0" class="mb-6">
        <!-- Insights Inteligentes -->
        <v-col cols="12" md="6" v-if="insights.length > 0">
          <IntelligentInsights
            :insights="insights"
            :loading="loadingInsights"
            @refresh="refreshAllData"
            @add-transaction="showNewLancamento = true"
          />
        </v-col>

        <!-- Alertas -->
        <v-col cols="12" md="6" v-if="alerts.length > 0">
          <v-card class="alert-card" elevation="4">
            <v-card-title class="d-flex align-center">
              <v-icon icon="mdi-alert" color="warning" class="me-2" />
              Alertas Importantes
            </v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item
                  v-for="alert in alerts.slice(0, 3)"
                  :key="alert.id"
                  class="alert-item"
                >
                  <template #prepend>
                    <v-icon :icon="alert.icon" :color="alert.severity" size="small" />
                  </template>
                  <v-list-item-title class="text-body-2">
                    {{ alert.title }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="text-caption">
                    {{ alert.message }}
                  </v-list-item-subtitle>
                  <template #append>
                    <v-btn
                      icon="mdi-close"
                      size="x-small"
                      variant="text"
                      @click="dismissAlert(alert.id)"
                    />
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Gráficos Simplificados -->
      <v-row class="charts-section mb-6">
        <!-- Gráfico de Evolução Temporal -->
        <v-col cols="12" lg="8">
          <v-card class="chart-card" elevation="4" height="400">
            <v-card-title class="d-flex justify-space-between align-center">
              <span>Evolução Financeira</span>
              <v-btn-toggle
                v-model="chartPeriod"
                variant="outlined"
                size="small"
                mandatory
              >
                <v-btn value="7d" size="small">7d</v-btn>
                <v-btn value="30d" size="small">30d</v-btn>
                <v-btn value="90d" size="small">90d</v-btn>
              </v-btn-toggle>
            </v-card-title>
            <v-card-text>
              <div v-if="loadingCharts" class="d-flex justify-center align-center" style="height: 300px;">
                <v-progress-circular indeterminate color="primary" />
              </div>
              <canvas v-else ref="evolutionChart" style="max-height: 300px;"></canvas>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Gráfico de Distribuição por Categoria -->
        <v-col cols="12" lg="4">
          <v-card class="chart-card" elevation="4" height="400">
            <v-card-title>Distribuição por Categoria</v-card-title>
            <v-card-text>
              <div v-if="loadingCharts" class="d-flex justify-center align-center" style="height: 300px;">
                <v-progress-circular indeterminate color="primary" />
              </div>
              <canvas v-else ref="categoryChart" style="max-height: 300px;"></canvas>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Transações Recentes -->
      <v-row class="activity-section">
        <v-col cols="12" lg="8">
          <v-card class="transactions-card" elevation="4">
            <v-card-title class="d-flex justify-space-between align-center">
              <span>Lançamentos Recentes</span>
              <v-btn
                variant="text"
                size="small"
                @click="$router.push('/lancamentos')"
              >
                Ver Todos
              </v-btn>
            </v-card-title>
            <v-card-text>
              <div v-if="loadingTransactions" class="text-center py-4">
                <v-progress-circular indeterminate color="primary" />
              </div>
              <v-list v-else-if="recentTransactions.length > 0" density="compact">
                <v-list-item
                  v-for="transaction in recentTransactions.slice(0, 5)"
                  :key="transaction.id"
                  class="transaction-item"
                >
                  <template #prepend>
                    <v-avatar :color="transaction.tipo === 'receita' ? 'success' : 'error'" size="32">
                      <v-icon 
                        :icon="transaction.tipo === 'receita' ? 'mdi-trending-up' : 'mdi-trending-down'" 
                        size="16"
                      />
                    </v-avatar>
                  </template>
                  <v-list-item-title>{{ transaction.descricao }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ formatDate(transaction.data) }} • {{ transaction.categoria }}
                  </v-list-item-subtitle>
                  <template #append>
                    <span 
                      :class="[
                        'font-weight-bold',
                        transaction.tipo === 'receita' ? 'text-success' : 'text-error'
                      ]"
                    >
                      {{ transaction.tipo === 'receita' ? '+' : '-' }}{{ formatCurrency(transaction.valor) }}
                    </span>
                  </template>
                </v-list-item>
              </v-list>
              <div v-else class="text-center py-4 text-medium-emphasis">
                <v-icon icon="mdi-file-document-outline" size="48" class="mb-2" />
                <p>Nenhum lançamento encontrado</p>
                <v-btn
                  color="primary"
                  variant="outlined"
                  @click="showNewLancamento = true"
                >
                  Criar Primeiro Lançamento
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Status do Sistema -->
        <v-col cols="12" lg="4">
          <v-card class="system-card" elevation="4">
            <v-card-title class="d-flex align-center">
              <v-icon icon="mdi-monitor-dashboard" class="me-2" />
              Status do Sistema
            </v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item>
                  <template #prepend>
                    <v-icon 
                      :icon="systemHealth >= 90 ? 'mdi-check-circle' : 'mdi-alert-circle'" 
                      :color="systemHealth >= 90 ? 'success' : 'warning'"
                    />
                  </template>
                  <v-list-item-title>Saúde do Sistema</v-list-item-title>
                  <v-list-item-subtitle>{{ systemHealth }}% - {{ getHealthStatus(systemHealth) }}</v-list-item-subtitle>
                </v-list-item>

                <v-list-item>
                  <template #prepend>
                    <v-icon icon="mdi-database" color="info" />
                  </template>
                  <v-list-item-title>Banco de Dados</v-list-item-title>
                  <v-list-item-subtitle>{{ systemStatus.database || 'Conectado' }}</v-list-item-subtitle>
                </v-list-item>

                <v-list-item>
                  <template #prepend>
                    <v-icon icon="mdi-robot" color="primary" />
                  </template>
                  <v-list-item-title>IA Assistant</v-list-item-title>
                  <v-list-item-subtitle>{{ systemStatus.ai || 'Online' }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>

              <v-btn
                block
                color="primary"
                variant="outlined"
                class="mt-4"
                @click="showChatbot = true"
              >
                <v-icon icon="mdi-chat" class="me-2" />
                Abrir Chat IA
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Modais -->
    <LancamentoForm
      v-model="showNewLancamento"
      @saved="handleTransactionSaved"
    />

    <ChatbotModal
      v-model="showChatbot"
    />

    <!-- FAB melhorado -->
    <v-fab
      icon="mdi-plus"
      location="bottom end"
      size="large"
      color="primary"
      @click="showNewLancamento = true"
      app
    />
  </div>
</template>

<script setup>
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

// Stores
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import { useNotificationStore } from '@/stores/notifications'

// Composables
import { useChartData } from '@/composables/useChartData'
import { useDashboardData } from '@/composables/useDashboardData'
import { useRealTimeUpdates } from '@/composables/useRealTimeUpdates'

// Componentes
import ChatbotModal from '@/components/ChatbotModal.vue'
import IntelligentInsights from '@/components/dashboard/IntelligentInsights.vue'
import MetricsGrid from '@/components/dashboard/MetricsGrid.vue'
import LancamentoForm from '@/components/LancamentoForm.vue'

// Chart.js imports
import {
    ArcElement,
    CategoryScale,
    Chart as ChartJS,
    Filler,
    Legend,
    LinearScale,
    LineElement,
    PointElement,
    Title,
    Tooltip
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

// Stores
const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const notificationStore = useNotificationStore()
const router = useRouter()

// Composables
const {
  summary,
  insights,
  alerts,
  trendData,
  loading,
  refreshAllData,
  dismissAlert
} = useDashboardData()

const {
  evolutionData,
  categoryData,
  chartPeriod,
  loadingCharts,
  refreshChartData
} = useChartData()

const {
  recentTransactions,
  systemStatus,
  systemHealth,
  loadingTransactions
} = useRealTimeUpdates()

// Estados locais
const showNewLancamento = ref(false)
const showChatbot = ref(false)

// Chart refs
const evolutionChart = ref(null)
const categoryChart = ref(null)
let evolutionChartInstance = null
let categoryChartInstance = null

// Métodos
const handleTransactionSaved = () => {
  showNewLancamento.value = false
  refreshAllData()
  try {
  notificationStore.showSuccess('Lançamento salvo com sucesso!')
  } catch (error) {
    console.log('Lançamento salvo com sucesso!')
  }
}

const handleInsightClick = (insight) => {
  if (notificationStore) {
  notificationStore.showInfo(insight.description)
  }
}

const handleMetricAction = (action) => {
  switch (action.key) {
    case 'new-receita':
      showNewLancamento.value = true
      break
    case 'view-categories':
      router.push('/categorias')
      break
    case 'view-goals':
      router.push('/metas')
      break
    case 'analytics':
      // Implementar analytics específicos
      break
  }
}

const formatDate = (date) => {
  return format(new Date(date), 'dd/MM/yyyy', { locale: ptBR })
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value)
}

const getHealthStatus = (health) => {
  if (health >= 90) return 'Excelente'
  if (health >= 70) return 'Bom'
  if (health >= 50) return 'Regular'
  return 'Crítico'
}

// Chart creation functions
const createEvolutionChart = () => {
  if (!evolutionChart.value || !evolutionData.value) return

  try {
  const ctx = evolutionChart.value.getContext('2d')
  
  if (evolutionChartInstance) {
    evolutionChartInstance.destroy()
  }

  evolutionChartInstance = new ChartJS(ctx, {
    type: 'line',
    data: {
      labels: evolutionData.value.labels || [],
      datasets: [
        {
          label: 'Receitas',
          data: evolutionData.value.receitas || [],
          borderColor: 'rgb(76, 175, 80)',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Despesas',
          data: evolutionData.value.despesas || [],
          borderColor: 'rgb(244, 67, 54)',
          backgroundColor: 'rgba(244, 67, 54, 0.1)',
          fill: true,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL',
                minimumFractionDigits: 0
              }).format(value)
            }
          }
        }
      }
    }
  })
  } catch (error) {
    console.error('Error creating evolution chart:', error)
  }
}

const createCategoryChart = () => {
  if (!categoryChart.value || !categoryData.value) return

  try {
  const ctx = categoryChart.value.getContext('2d')
  
  if (categoryChartInstance) {
    categoryChartInstance.destroy()
  }

  categoryChartInstance = new ChartJS(ctx, {
    type: 'doughnut',
    data: {
      labels: categoryData.value.labels || [],
      datasets: [{
        data: categoryData.value.values || [],
        backgroundColor: [
          'rgba(76, 175, 80, 0.8)',
          'rgba(33, 150, 243, 0.8)',
          'rgba(255, 152, 0, 0.8)',
          'rgba(156, 39, 176, 0.8)',
          'rgba(244, 67, 54, 0.8)',
          'rgba(96, 125, 139, 0.8)'
        ],
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
        }
      }
    }
  })
  } catch (error) {
    console.error('Error creating category chart:', error)
  }
}

// Watchers
watch(() => evolutionData.value, () => {
  nextTick(() => createEvolutionChart())
}, { deep: true })

watch(() => categoryData.value, () => {
  nextTick(() => createCategoryChart())
}, { deep: true })

watch(chartPeriod, () => {
  refreshChartData()
})

// Lifecycle
onMounted(async () => {
  try {
  if (authStore.isAuthenticated) {
    await refreshAllData()
    await refreshChartData()
    
    nextTick(() => {
      createEvolutionChart()
      createCategoryChart()
    })
    } else {
      console.warn('User not authenticated, redirecting to login')
      router.push('/auth/login')
    }
  } catch (error) {
    console.error('Error loading dashboard:', error)
    if (notificationStore) {
      notificationStore.showError('Erro ao carregar dashboard')
    }
  }
})
</script>

<style lang="scss" scoped>
.biuai-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.dashboard-header {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

// Cards com glassmorphism
.insight-card,
.alert-card,
.chart-card,
.transactions-card,
.system-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }
}

// Items com hover
.insight-item,
.alert-item,
.transaction-item {
  border-radius: 8px;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }
}

// Responsive
@media (max-width: 960px) {
  .header-actions {
    .v-btn:not(.v-btn--icon) {
      .v-btn__content {
        display: none;
      }
    }
  }
}

@media (max-width: 600px) {
  .dashboard-header {
    height: 64px !important;
    
    .header-info h1 {
      font-size: 1.5rem !important;
    }
  }
  
  .charts-section .v-col,
  .activity-section .v-col {
    margin-bottom: 1rem;
  }
}

// Dark theme
.v-theme--dark {
  .biuai-dashboard {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  }
  
  .dashboard-header {
    background: rgba(30, 30, 46, 0.95) !important;
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }
  
  .insight-card,
  .alert-card,
  .chart-card,
  .transactions-card,
  .system-card {
    background: rgba(30, 30, 46, 0.95);
    border-color: rgba(255, 255, 255, 0.1);
  }
}
</style> 