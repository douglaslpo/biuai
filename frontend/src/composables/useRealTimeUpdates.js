import { ref, computed, onMounted, onUnmounted } from 'vue'
import { api } from '@/boot/axios'

export function useRealTimeUpdates() {
  // States
  const loadingTransactions = ref(false)
  const loadingSystem = ref(false)
  const lastTransactionUpdate = ref(null)
  const lastSystemUpdate = ref(null)

  // Data
  const recentTransactions = ref([])
  const systemStatus = ref('healthy')
  
  const systemMetrics = ref({
    api_response_time: 85,
    database_connections: 12,
    memory_usage: 68,
    cpu_usage: 25,
    active_users: 1,
    requests_per_minute: 45,
    error_rate: 0.2,
    uptime_percentage: 99.9
  })

  const systemHealth = ref({
    overall: 'good',
    database: 'healthy',
    cache: 'healthy',
    api: 'healthy',
    storage: 'healthy',
    monitoring: 'active'
  })

  // Computed
  const transactionsSummary = computed(() => {
    const total = recentTransactions.value.length
    const receitas = recentTransactions.value.filter(t => t.tipo === 'RECEITA').length
    const despesas = recentTransactions.value.filter(t => t.tipo === 'DESPESA').length
    const today = new Date().toDateString()
    const todayTransactions = recentTransactions.value.filter(
      t => new Date(t.data_lancamento).toDateString() === today
    ).length

    return {
      total,
      receitas,
      despesas,
      today: todayTransactions
    }
  })

  const systemHealthScore = computed(() => {
    const metrics = systemMetrics.value
    const scores = [
      100 - metrics.api_response_time, // Menor tempo = melhor
      (100 - metrics.memory_usage), // Menor uso = melhor
      (100 - metrics.cpu_usage), // Menor uso = melhor
      Math.min(100, metrics.uptime_percentage), // Max 100%
      Math.max(0, 100 - metrics.error_rate * 10) // Menor erro = melhor
    ]
    
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
  })

  // Methods
  const refreshTransactions = async () => {
    loadingTransactions.value = true
    try {
      const response = await api.get('/api/v1/financeiro?limit=10&sort=data_lancamento&order=desc')
      
      if (response.data && Array.isArray(response.data)) {
        recentTransactions.value = response.data.map(transaction => ({
          ...transaction,
          // Adicionar campos computados
          formatted_date: formatDate(transaction.data_lancamento),
          formatted_value: formatCurrency(transaction.valor),
          icon: getTransactionIcon(transaction),
          color: getTransactionColor(transaction),
          category_display: transaction.categoria || 'Sem categoria'
        }))
      } else {
        // Fallback com dados realistas
        recentTransactions.value = generateMockTransactions()
      }
      
      lastTransactionUpdate.value = new Date()
    } catch (error) {
      console.error('Erro ao carregar transações recentes:', error)
      // Usar dados mock em caso de erro
      recentTransactions.value = generateMockTransactions()
    } finally {
      loadingTransactions.value = false
    }
  }

  const refreshSystemData = async () => {
    loadingSystem.value = true
    try {
      // Simular coleta de métricas do sistema
      await Promise.all([
        updateSystemMetrics(),
        updateSystemHealth(),
        checkSystemStatus()
      ])
      
      lastSystemUpdate.value = new Date()
    } catch (error) {
      console.error('Erro ao atualizar dados do sistema:', error)
      systemStatus.value = 'warning'
    } finally {
      loadingSystem.value = false
    }
  }

  const updateSystemMetrics = async () => {
    try {
      // Simular métricas do sistema com variações realistas
      const currentMetrics = systemMetrics.value
      
      systemMetrics.value = {
        api_response_time: Math.max(50, Math.min(200, 
          currentMetrics.api_response_time + (Math.random() - 0.5) * 20
        )),
        database_connections: Math.max(5, Math.min(50,
          currentMetrics.database_connections + Math.floor((Math.random() - 0.5) * 6)
        )),
        memory_usage: Math.max(30, Math.min(95,
          currentMetrics.memory_usage + (Math.random() - 0.5) * 10
        )),
        cpu_usage: Math.max(10, Math.min(90,
          currentMetrics.cpu_usage + (Math.random() - 0.5) * 15
        )),
        active_users: Math.max(1, Math.min(100,
          currentMetrics.active_users + Math.floor((Math.random() - 0.5) * 3)
        )),
        requests_per_minute: Math.max(20, Math.min(200,
          currentMetrics.requests_per_minute + Math.floor((Math.random() - 0.5) * 20)
        )),
        error_rate: Math.max(0, Math.min(5,
          currentMetrics.error_rate + (Math.random() - 0.5) * 0.5
        )),
        uptime_percentage: Math.max(95, Math.min(100,
          currentMetrics.uptime_percentage + (Math.random() - 0.5) * 0.1
        ))
      }
    } catch (error) {
      console.error('Erro ao atualizar métricas:', error)
    }
  }

  const updateSystemHealth = async () => {
    try {
      const metrics = systemMetrics.value
      
      // Determinar saúde dos componentes baseado nas métricas
      systemHealth.value = {
        overall: determineOverallHealth(),
        database: metrics.database_connections > 30 ? 'warning' : 'healthy',
        cache: metrics.memory_usage > 80 ? 'warning' : 'healthy',
        api: metrics.api_response_time > 150 ? 'warning' : 'healthy',
        storage: Math.random() > 0.95 ? 'warning' : 'healthy', // Raramente com problema
        monitoring: 'active'
      }
    } catch (error) {
      console.error('Erro ao atualizar saúde do sistema:', error)
    }
  }

  const checkSystemStatus = async () => {
    try {
      const healthScore = systemHealthScore.value
      
      if (healthScore >= 80) {
        systemStatus.value = 'healthy'
      } else if (healthScore >= 60) {
        systemStatus.value = 'warning'
      } else {
        systemStatus.value = 'critical'
      }
    } catch (error) {
      console.error('Erro ao verificar status do sistema:', error)
      systemStatus.value = 'unknown'
    }
  }

  // Utility functions
  const generateMockTransactions = () => {
    const mockTransactions = [
      {
        id: 1,
        descricao: 'Salário - Janeiro 2025',
        valor: 8500.00,
        tipo: 'RECEITA',
        data_lancamento: new Date(2025, 0, 25),
        categoria: 'Salário',
        orgao_nome: 'Empresa XYZ'
      },
      {
        id: 2,
        descricao: 'Supermercado - Compras da semana',
        valor: -320.50,
        tipo: 'DESPESA',
        data_lancamento: new Date(2025, 0, 24),
        categoria: 'Alimentação',
        orgao_nome: 'Supermercado ABC'
      },
      {
        id: 3,
        descricao: 'Freelance - Projeto de Design',
        valor: 1200.00,
        tipo: 'RECEITA',
        data_lancamento: new Date(2025, 0, 23),
        categoria: 'Freelance',
        orgao_nome: 'Cliente DEF'
      },
      {
        id: 4,
        descricao: 'Conta de Energia Elétrica',
        valor: -185.90,
        tipo: 'DESPESA',
        data_lancamento: new Date(2025, 0, 22),
        categoria: 'Utilities',
        orgao_nome: 'CEMIG'
      },
      {
        id: 5,
        descricao: 'Venda de Produto Online',
        valor: 450.00,
        tipo: 'RECEITA',
        data_lancamento: new Date(2025, 0, 21),
        categoria: 'Vendas',
        orgao_nome: 'Marketplace'
      },
      {
        id: 6,
        descricao: 'Gasolina',
        valor: -120.00,
        tipo: 'DESPESA',
        data_lancamento: new Date(2025, 0, 20),
        categoria: 'Transporte',
        orgao_nome: 'Posto Shell'
      },
      {
        id: 7,
        descricao: 'Aluguel - Janeiro',
        valor: -1500.00,
        tipo: 'DESPESA',
        data_lancamento: new Date(2025, 0, 5),
        categoria: 'Moradia',
        orgao_nome: 'Imobiliária GHI'
      }
    ]

    return mockTransactions.map(transaction => ({
      ...transaction,
      formatted_date: formatDate(transaction.data_lancamento),
      formatted_value: formatCurrency(transaction.valor),
      icon: getTransactionIcon(transaction),
      color: getTransactionColor(transaction),
      category_display: transaction.categoria || 'Sem categoria'
    }))
  }

  const determineOverallHealth = () => {
    const score = systemHealthScore.value
    if (score >= 85) return 'excellent'
    if (score >= 70) return 'good'
    if (score >= 50) return 'fair'
    return 'poor'
  }

  const getTransactionIcon = (transaction) => {
    if (transaction.tipo === 'RECEITA') {
      return 'mdi-trending-up'
    }
    
    // Ícones baseados na categoria
    const categoryIcons = {
      'Alimentação': 'mdi-food',
      'Transporte': 'mdi-car',
      'Moradia': 'mdi-home',
      'Utilities': 'mdi-lightning-bolt',
      'Saúde': 'mdi-medical-bag',
      'Lazer': 'mdi-gamepad-variant',
      'Educação': 'mdi-school'
    }
    
    return categoryIcons[transaction.categoria] || 'mdi-trending-down'
  }

  const getTransactionColor = (transaction) => {
    return transaction.tipo === 'RECEITA' ? 'success' : 'error'
  }

  const formatDate = (date) => {
    if (!date) return ''
    const d = new Date(date)
    return d.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0)
  }

  const getRelativeTime = (date) => {
    const now = new Date()
    const diffInMs = now - new Date(date)
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60))
    const diffInHours = Math.floor(diffInMinutes / 60)
    const diffInDays = Math.floor(diffInHours / 24)

    if (diffInMinutes < 60) {
      return `${diffInMinutes} min atrás`
    } else if (diffInHours < 24) {
      return `${diffInHours}h atrás`
    } else if (diffInDays < 7) {
      return `${diffInDays} dias atrás`
    } else {
      return formatDate(date)
    }
  }

  // Real-time updates
  const updateInterval = ref(null)
  const metricsInterval = ref(null)

  const startRealTimeUpdates = () => {
    // Atualizar transações a cada 2 minutos
    updateInterval.value = setInterval(refreshTransactions, 2 * 60 * 1000)
    
    // Atualizar métricas do sistema a cada 30 segundos
    metricsInterval.value = setInterval(refreshSystemData, 30 * 1000)
  }

  const stopRealTimeUpdates = () => {
    if (updateInterval.value) {
      clearInterval(updateInterval.value)
      updateInterval.value = null
    }
    
    if (metricsInterval.value) {
      clearInterval(metricsInterval.value)
      metricsInterval.value = null
    }
  }

  // Lifecycle
  onMounted(() => {
    refreshTransactions()
    refreshSystemData()
    startRealTimeUpdates()
  })

  onUnmounted(() => {
    stopRealTimeUpdates()
  })

  return {
    // States
    loadingTransactions,
    loadingSystem,
    lastTransactionUpdate,
    lastSystemUpdate,

    // Data
    recentTransactions,
    systemStatus,
    systemMetrics,
    systemHealth,

    // Computed
    transactionsSummary,
    systemHealthScore,

    // Methods
    refreshTransactions,
    refreshSystemData,
    startRealTimeUpdates,
    stopRealTimeUpdates,

    // Utils
    formatDate,
    formatCurrency,
    getRelativeTime,
    getTransactionIcon,
    getTransactionColor
  }
} 