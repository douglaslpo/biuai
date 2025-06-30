<template>
  <div class="biuai-dashboard">
    <!-- Header da página com botões mais visíveis -->
    <div class="dashboard-header mb-6">
      <div class="header-content">
        <div class="header-info">
          <h1 class="dashboard-title">
            💼 Dashboard Financeiro
          </h1>
          <p class="dashboard-subtitle">
            Bem-vindo de volta, {{ authStore.user?.full_name || 'Usuário' }}! 
            <v-chip color="success" size="small" variant="elevated" class="ml-2">
              <v-icon start icon="mdi-check-circle" size="small" />
              Sistema Online
            </v-chip>
          </p>
        </div>
        
        <div class="header-actions">
          <v-btn
            color="primary"
            size="large"
            variant="elevated"
            prepend-icon="mdi-plus"
            @click="showNewLancamento = true"
            class="new-lancamento-btn"
          >
            <span class="font-weight-bold">Novo Lançamento</span>
          </v-btn>
          
          <v-btn
            color="secondary"
            size="large"
            variant="outlined"
            :loading="loading"
            @click="refreshData"
            class="refresh-btn"
          >
            <v-icon>mdi-refresh</v-icon>
          </v-btn>
          
          <v-btn
            color="info"
            size="large"
            variant="tonal"
            prepend-icon="mdi-cloud-download"
            :loading="importing"
            @click="importSiogData"
            class="import-btn"
          >
            <span class="font-weight-medium">Importar SIOG</span>
          </v-btn>
        </div>
      </div>
    </div>

    <!-- Cards de métricas principais com melhor contraste -->
    <v-row class="metrics-row mb-6">
      <v-col cols="12" md="4">
        <v-card
          class="metric-card metric-card--success"
          elevation="8"
          hover
        >
          <v-card-text class="pa-6">
            <div class="d-flex align-center justify-space-between">
              <div class="metric-content">
                <div class="metric-icon-wrapper mb-3">
                  <v-icon icon="mdi-trending-up" size="32" class="metric-icon" />
                </div>
                <div class="metric-label">💰 Receitas</div>
                <div class="metric-value">
                  {{ formatCurrency(summary.total_receitas) }}
                </div>
                <div class="metric-subtitle">
                  {{ summary.total_receitas_count || 0 }} lançamentos • {{ summary.periodo_dias }} dias
                </div>
              </div>
              <div class="metric-visual">
                <v-progress-circular
                  :model-value="75"
                  size="60"
                  width="6"
                  color="white"
                  class="metric-progress"
                />
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card
          class="metric-card metric-card--error"
          elevation="8"
          hover
        >
          <v-card-text class="pa-6">
            <div class="d-flex align-center justify-space-between">
              <div class="metric-content">
                <div class="metric-icon-wrapper mb-3">
                  <v-icon icon="mdi-trending-down" size="32" class="metric-icon" />
                </div>
                <div class="metric-label">💸 Despesas</div>
                <div class="metric-value">
                  {{ formatCurrency(Math.abs(summary.total_despesas)) }}
                </div>
                <div class="metric-subtitle">
                  {{ summary.total_despesas_count || 0 }} lançamentos • {{ summary.periodo_dias }} dias
                </div>
              </div>
              <div class="metric-visual">
                <v-progress-circular
                  :model-value="85"
                  size="60"
                  width="6"
                  color="white"
                  class="metric-progress"
                />
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card
          :class="`metric-card ${summary.saldo >= 0 ? 'metric-card--info' : 'metric-card--warning'}`"
          elevation="8"
          hover
        >
          <v-card-text class="pa-6">
            <div class="d-flex align-center justify-space-between">
              <div class="metric-content">
                <div class="metric-icon-wrapper mb-3">
                  <v-icon 
                    :icon="summary.saldo >= 0 ? 'mdi-account-balance' : 'mdi-alert'" 
                    size="32" 
                    class="metric-icon" 
                  />
                </div>
                <div class="metric-label">⚖️ Saldo</div>
                <div class="metric-value">
                  {{ formatCurrency(summary.saldo) }}
                </div>
                <div class="metric-subtitle">
                  {{ summary.total_lancamentos }} lançamentos • {{ summary.saldo >= 0 ? 'Positivo' : 'Atenção' }}
                </div>
              </div>
              <div class="metric-visual">
                <v-progress-circular
                  :model-value="summary.saldo >= 0 ? 65 : 35"
                  size="60"
                  width="6"
                  color="white"
                  class="metric-progress"
                />
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Insights com IA -->
    <div v-if="aiInsights.length > 0" class="mb-6">
      <v-card elevation="4" class="insights-card">
        <v-card-title class="pa-6 pb-4">
          <v-icon icon="mdi-brain" color="primary" class="mr-3" />
          <span class="text-h5 font-weight-bold">🤖 Insights Financeiros com IA</span>
          <v-spacer />
          <v-chip color="primary" variant="tonal" size="small">
            Análises automáticas
          </v-chip>
        </v-card-title>
        <v-card-text class="pa-6 pt-0">
          <div class="d-flex flex-wrap ga-3">
            <v-chip
              v-for="insight in aiInsights"
              :key="insight.id"
              :color="getInsightColor(insight.type)"
              :prepend-icon="insight.icon"
              variant="elevated"
              size="large"
              clickable
              @click="showInsightDetails(insight)"
              class="insight-chip"
            >
              {{ insight.title }}
            </v-chip>
          </div>
        </v-card-text>
      </v-card>
    </div>

    <!-- Gráficos e Analytics com melhor layout -->
    <v-row class="charts-row mb-6">
      <!-- Gráfico de evolução -->
      <v-col cols="12" lg="8">
        <v-card elevation="4" class="chart-card">
          <v-card-title class="pa-6 pb-4">
            <v-icon icon="mdi-chart-line" color="primary" class="mr-3" />
            <span class="text-h5 font-weight-bold">📈 Evolução Financeira</span>
            <v-spacer />
            <v-chip color="success" variant="tonal" size="small">
              Últimos meses
            </v-chip>
          </v-card-title>
          <v-card-text class="pa-6 pt-0">
            <div class="chart-container">
              <canvas ref="evolutionChart"></canvas>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Distribuição por categoria -->
      <v-col cols="12" lg="4">
        <v-card elevation="4" class="chart-card">
          <v-card-title class="pa-6 pb-4">
            <v-icon icon="mdi-chart-donut" color="primary" class="mr-3" />
            <span class="text-h6 font-weight-bold">🏷️ Distribuição</span>
          </v-card-title>
          <v-card-text class="pa-6 pt-0">
            <div class="chart-container chart-container--donut">
              <canvas ref="categoryChart"></canvas>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Lançamentos recentes e MCP Widget -->
    <v-row>
      <!-- Lançamentos recentes -->
      <v-col cols="12" lg="8">
        <BaseCard
          title="🕒 Lançamentos Recentes"
          subtitle="Últimas movimentações financeiras"
          icon="mdi-clock-outline"
          hover
        >
          <template #actions>
            <BaseButton
              variant="text"
              size="small"
              @click="$router.push('/lancamentos')"
            >
              Ver todos
            </BaseButton>
          </template>

          <v-list v-if="recentLancamentos.length > 0" class="pa-0">
            <v-list-item
              v-for="lancamento in recentLancamentos"
              :key="lancamento.id"
              @click="editLancamento(lancamento)"
              class="rounded-lg mb-2"
              color="primary"
            >
              <template #prepend>
                <v-avatar 
                  :color="lancamento.tipo === 'RECEITA' ? 'success' : 'error'"
                  size="40"
                >
                  <v-icon 
                    :icon="lancamento.tipo === 'RECEITA' ? 'mdi-plus' : 'mdi-minus'"
                    color="white"
                  />
                </v-avatar>
              </template>

              <v-list-item-title class="font-weight-medium">
                {{ lancamento.descricao }}
              </v-list-item-title>
              <v-list-item-subtitle>
                {{ formatDate(lancamento.data_lancamento) }} • 
                {{ lancamento.categoria || 'Sem categoria' }}
              </v-list-item-subtitle>

              <template #append>
                <div class="text-end">
                  <div 
                    class="font-weight-bold"
                    :class="lancamento.tipo === 'RECEITA' ? 'text-success' : 'text-error'"
                  >
                    {{ formatCurrency(lancamento.valor) }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ lancamento.orgao_nome }}
                  </div>
                </div>
              </template>
            </v-list-item>
          </v-list>

          <div v-else class="text-center py-8">
            <v-icon icon="mdi-information-outline" size="64" color="grey" class="mb-4" />
            <p class="text-body-1 text-medium-emphasis">
              Nenhum lançamento encontrado
            </p>
            <BaseButton
              type="primary"
              prepend-icon="mdi-plus"
              @click="showNewLancamento = true"
            >
              Criar Primeiro Lançamento
            </BaseButton>
          </div>
        </BaseCard>
      </v-col>

      <!-- MCP Widget para monitoramento -->
      <v-col cols="12" lg="4">
        <MCPWidget
          title="Status do Sistema"
          type="status"
          :status="systemStatus"
          :metrics="systemMetrics"
          :items="systemItems"
          :refreshable="true"
          :auto-refresh="30"
          @refresh="refreshSystemData"
          class="mb-4"
        />

        <!-- KPIs adicionais -->
        <BaseCard
          title="📊 KPIs do Mês"
          subtitle="Indicadores principais"
          icon="mdi-speedometer"
          type="info"
          hover
        >
          <v-list density="compact" class="pa-0">
            <v-list-item>
              <template #prepend>
                <v-icon icon="mdi-target" color="primary" />
              </template>
              <v-list-item-title>Meta de Economia</v-list-item-title>
              <template #append>
                <v-chip 
                  :color="monthlyGoal.achieved ? 'success' : 'warning'" 
                  size="small"
                  variant="flat"
                >
                  {{ monthlyGoal.percentage }}%
                </v-chip>
              </template>
            </v-list-item>

            <v-list-item>
              <template #prepend>
                <v-icon icon="mdi-chart-timeline-variant" color="success" />
              </template>
              <v-list-item-title>Crescimento</v-list-item-title>
              <template #append>
                <span class="font-weight-bold text-success">
                  +{{ growth.percentage }}%
                </span>
              </template>
            </v-list-item>

            <v-list-item>
              <template #prepend>
                <v-icon icon="mdi-calendar-month" color="info" />
              </template>
              <v-list-item-title>Dias restantes</v-list-item-title>
              <template #append>
                <span class="font-weight-bold">
                  {{ daysRemainingInMonth }}
                </span>
              </template>
            </v-list-item>
          </v-list>
        </BaseCard>
      </v-col>
    </v-row>

    <!-- Dialogs -->
    <LancamentoForm
      v-model="showNewLancamento"
      @saved="handleLancamentoSaved"
    />

    <!-- Floating Action Button -->
    <v-fab
      icon="mdi-plus"
      location="bottom end"
      size="large"
      color="primary"
      @click="showNewLancamento = true"
      class="biuai-fab"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useLancamentosStore } from '@/stores/lancamentos'
import BaseCard from '@/components/base/BaseCard.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import MCPWidget from '@/components/MCPWidget.vue'
import LancamentoForm from '@/components/LancamentoForm.vue'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import Chart from 'chart.js/auto'

// Stores
const authStore = useAuthStore()
const lancamentosStore = useLancamentosStore()
const router = useRouter()

// Estados reativos
const loading = ref(false)
const importing = ref(false)
const showNewLancamento = ref(false)
const evolutionChart = ref(null)
const categoryChart = ref(null)
const refreshInterval = ref(null)

// Dados do dashboard
const summary = ref({
  total_receitas: 0,
  total_despesas: 0,
  saldo: 0,
  total_lancamentos: 0,
  periodo_dias: 30,
  total_receitas_count: 0,
  total_despesas_count: 0
})

const recentLancamentos = ref([])
const aiInsights = ref([
  {
    id: 1,
    title: 'Gastos elevados esta semana',
    type: 'warning',
    icon: 'mdi-alert-circle',
    description: 'Seus gastos aumentaram 15% comparado à semana passada'
  },
  {
    id: 2,
    title: 'Meta de economia atingida',
    type: 'positive',
    icon: 'mdi-target',
    description: 'Parabéns! Você atingiu sua meta de economia do mês'
  },
  {
    id: 3,
    title: 'Nova categoria detectada',
    type: 'info',
    icon: 'mdi-tag',
    description: 'Detectamos gastos em uma nova categoria: Educação'
  }
])

// Sistema de monitoramento
const systemStatus = ref('success')
const systemMetrics = computed(() => [
  {
    name: 'performance',
    label: 'Performance API',
    value: 95,
    format: 'percentage',
    color: 'success'
  },
  {
    name: 'uptime',
    label: 'Tempo Online',
    value: 99.9,
    format: 'percentage',
    color: 'success'
  }
])

const systemItems = computed(() => [
  {
    title: 'Backend API',
    subtitle: 'Funcionando normalmente',
    icon: 'mdi-server',
    color: 'success',
    value: 'Online'
  },
  {
    title: 'Base de Dados',
    subtitle: 'PostgreSQL conectado',
    icon: 'mdi-database',
    color: 'success',
    value: 'OK'
  },
  {
    title: 'Cache Redis',
    subtitle: 'Cache ativo',
    icon: 'mdi-memory',
    color: 'success',
    value: 'Ativo'
  },
  {
    title: 'Monitoramento',
    subtitle: 'SigNoz coletando dados',
    icon: 'mdi-monitor-eye',
    color: 'info',
    value: 'Ativo'
  }
])

// KPIs
const monthlyGoal = ref({
  target: 5000,
  current: 3750,
  achieved: false,
  percentage: 75
})

const growth = ref({
  percentage: 12.5,
  trend: 'up'
})

const daysRemainingInMonth = computed(() => {
  const now = new Date()
  const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  return lastDay.getDate() - now.getDate()
})

// Refs dos gráficos
let evolutionChartInstance = null
let categoryChartInstance = null

// Métodos de formatação
const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value || 0)
}

const formatDate = (date) => {
  if (!date) return ''
  return format(new Date(date), 'dd/MM/yyyy', { locale: ptBR })
}

const getInsightColor = (type) => {
  const colors = {
    positive: 'success',
    warning: 'warning',
    info: 'info'
  }
  return colors[type] || 'grey'
}

// Métodos de ação
const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadSummary(),
      loadRecentLancamentos(),
      loadChartData()
    ])
  } finally {
    loading.value = false
  }
}

const loadSummary = async () => {
  try {
    const data = await lancamentosStore.getSummary()
    summary.value = { ...summary.value, ...data }
  } catch (error) {
    console.error('Erro ao carregar resumo:', error)
  }
}

const loadRecentLancamentos = async () => {
  try {
    const data = await lancamentosStore.getRecent(5)
    recentLancamentos.value = data
  } catch (error) {
    console.error('Erro ao carregar lançamentos recentes:', error)
  }
}

const loadChartData = async () => {
  try {
    // Carrega dados para os gráficos
    const evolutionData = await lancamentosStore.getEvolutionData()
    const categoryData = await lancamentosStore.getCategoryData()
    
    // Aguarda o próximo tick para garantir que os elementos canvas estejam montados
    await nextTick()
    
    // Inicializa gráfico de evolução
    if (evolutionChart.value && evolutionData) {
      initEvolutionChart(evolutionData)
    }
    
    // Inicializa gráfico de categorias
    if (categoryChart.value && categoryData) {
      initCategoryChart(categoryData)
    }
  } catch (error) {
    console.error('Erro ao carregar dados dos gráficos:', error)
  }
}

const initEvolutionChart = (data) => {
  if (evolutionChartInstance) {
    evolutionChartInstance.destroy()
  }
  
  const ctx = evolutionChart.value.getContext('2d')
  
  evolutionChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.labels || [],
      datasets: [
        {
          label: 'Receitas',
          data: data.receitas || [],
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4
        },
        {
          label: 'Despesas',
          data: data.despesas || [],
          borderColor: '#F44336',
          backgroundColor: 'rgba(244, 67, 54, 0.1)',
          borderWidth: 3,
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
          labels: {
            usePointStyle: true,
            padding: 20,
            font: {
              size: 12,
              weight: '500'
            }
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: '#fff',
          borderWidth: 1,
          callbacks: {
            label: function(context) {
              return context.dataset.label + ': ' + formatCurrency(context.parsed.y)
            }
          }
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Período'
          },
          grid: {
            display: false
          }
        },
        y: {
          display: true,
          title: {
            display: true,
            text: 'Valor (R$)'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            callback: function(value) {
              return formatCurrency(value)
            }
          }
        }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      }
    }
  })
}

const initCategoryChart = (data) => {
  if (categoryChartInstance) {
    categoryChartInstance.destroy()
  }
  
  const ctx = categoryChart.value.getContext('2d')
  
  categoryChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.labels || ['Receitas', 'Despesas'],
      datasets: [{
        data: data.values || [0, 0],
        backgroundColor: [
          '#4CAF50',
          '#F44336'
        ],
        borderWidth: 0,
        hoverBorderWidth: 2,
        hoverBorderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            usePointStyle: true,
            padding: 20,
            font: {
              size: 12,
              weight: '500'
            }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: '#fff',
          borderWidth: 1,
          callbacks: {
            label: function(context) {
              const total = context.dataset.data.reduce((a, b) => Math.abs(a) + Math.abs(b), 0)
              const percentage = total > 0 ? ((Math.abs(context.parsed) / total) * 100).toFixed(1) : 0
              return context.label + ': ' + formatCurrency(context.parsed) + ' (' + percentage + '%)'
            }
          }
        }
      },
      cutout: '60%'
    }
  })
}

const importSiogData = async () => {
  importing.value = true
  try {
    // Implementar importação SIOG
    await new Promise(resolve => setTimeout(resolve, 3000))
    await refreshData()
  } finally {
    importing.value = false
  }
}

const editLancamento = (lancamento) => {
  router.push(`/lancamentos/${lancamento.id}/edit`)
}

const handleLancamentoSaved = () => {
  showNewLancamento.value = false
  refreshData()
}

const showInsightDetails = (insight) => {
  // Implementar modal de detalhes do insight
  console.log('Insight selecionado:', insight)
}

const refreshSystemData = () => {
  // Atualizar dados do sistema
  console.log('Atualizando dados do sistema...')
}

// Lifecycle
onMounted(async () => {
  await refreshData()
  
  // Auto-refresh a cada 5 minutos
  refreshInterval.value = setInterval(refreshData, 5 * 60 * 1000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  
  // Limpa instâncias dos gráficos
  if (evolutionChartInstance) {
    evolutionChartInstance.destroy()
  }
  if (categoryChartInstance) {
    categoryChartInstance.destroy()
  }
})
</script>

<style lang="scss" scoped>
.biuai-dashboard {
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
  background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%);
  min-height: 100vh;
}

// Header melhorado
.dashboard-header {
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1.5rem;
    
    .header-info {
      .dashboard-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: rgb(var(--v-theme-primary));
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }
      
      .dashboard-subtitle {
        font-size: 1.1rem;
        color: rgba(var(--v-theme-on-surface), 0.7);
        font-weight: 500;
      }
    }
    
    .header-actions {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      
      .new-lancamento-btn {
        background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, #1976D2 100%);
        box-shadow: 0 4px 16px rgba(var(--v-theme-primary), 0.4);
        transform: translateY(0);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(var(--v-theme-primary), 0.6);
        }
      }
      
      .refresh-btn, .import-btn {
        border-width: 2px;
        font-weight: 600;
        transition: all 0.3s ease;
        
        &:hover {
          transform: translateY(-1px);
        }
      }
    }
  }
}

// Cards de métricas redesenhados
.metrics-row {
  .metric-card {
    border-radius: 16px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
    }
    
    .metric-content {
      .metric-icon-wrapper {
        .metric-icon {
          color: white;
          opacity: 0.9;
        }
      }
      
      .metric-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      
      .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
      }
      
      .metric-subtitle {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.8);
        font-weight: 500;
      }
    }
    
    .metric-visual {
      .metric-progress {
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
      }
    }
    
    &.metric-card--success {
      background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
    }
    
    &.metric-card--error {
      background: linear-gradient(135deg, #F44336 0%, #C62828 100%);
    }
    
    &.metric-card--info {
      background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
    }
    
    &.metric-card--warning {
      background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
    }
  }
}

// Insights card
.insights-card {
  border-radius: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border: 1px solid rgba(var(--v-theme-primary), 0.1);
  
  .insight-chip {
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }
  }
}

// Charts
.charts-row {
  .chart-card {
    border-radius: 16px;
    background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
    border: 1px solid rgba(var(--v-theme-primary), 0.1);
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
    }
    
    .chart-container {
      position: relative;
      width: 100%;
      height: 400px;
      
      &.chart-container--donut {
        height: 300px;
      }
      
      canvas {
        width: 100% !important;
        height: 100% !important;
        border-radius: 8px;
      }
    }
  }
}

// Floating Action Button
.biuai-fab {
  :deep(.v-fab) {
    background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, #1976D2 100%);
    box-shadow: 0 8px 24px rgba(var(--v-theme-primary), 0.4);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 32px rgba(var(--v-theme-primary), 0.6);
    }
  }
}

// Animações
.metric-card {
  animation: slideInUp 0.6s cubic-bezier(0.25, 0.8, 0.25, 1);
  
  &:nth-child(2) {
    animation-delay: 0.1s;
  }
  
  &:nth-child(3) {
    animation-delay: 0.2s;
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// Responsividade
@media (max-width: 960px) {
  .biuai-dashboard {
    padding: 1rem;
  }
  
  .dashboard-header .header-content {
    flex-direction: column;
    align-items: flex-start;
    
    .header-actions {
      width: 100%;
      justify-content: flex-start;
    }
  }
  
  .metrics-row .metric-card .metric-content .metric-value {
    font-size: 1.8rem;
  }
}

@media (max-width: 600px) {
  .header-actions {
    flex-direction: column;
    width: 100%;
    
    .v-btn {
      width: 100%;
      justify-content: center;
    }
  }
  
  .dashboard-header .header-info .dashboard-title {
    font-size: 2rem;
  }
  
  .metrics-row .metric-card .metric-content .metric-value {
    font-size: 1.6rem;
  }
  
  .charts-row .chart-card .chart-container {
    height: 300px;
    
    &.chart-container--donut {
      height: 250px;
    }
  }
}
</style> 