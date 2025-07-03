import { computed } from 'vue'

export function useMetrics(data, config = {}) {
  const {
    currency = 'BRL',
    locale = 'pt-BR'
  } = config

  // Formatters
  const formatCurrency = (value) => {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency
    }).format(value || 0)
  }

  const formatNumber = (value) => {
    return new Intl.NumberFormat(locale).format(value || 0)
  }

  const formatPercentage = (value, decimals = 1) => {
    return `${(value || 0).toFixed(decimals)}%`
  }

  const formatDate = (date) => {
    if (!date) return '-'
    return new Intl.DateTimeFormat(locale, {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    }).format(new Date(date))
  }

  // Basic calculations
  const calculateTotal = (items, field) => {
    return items.reduce((sum, item) => sum + (Number(item[field]) || 0), 0)
  }

  const calculateAverage = (items, field) => {
    if (!items.length) return 0
    return calculateTotal(items, field) / items.length
  }

  const calculateGrowth = (current, previous) => {
    if (!previous || previous === 0) return 0
    return ((current - previous) / previous) * 100
  }

  const calculateGrowthTrend = (current, previous) => {
    const growth = calculateGrowth(current, previous)
    
    if (growth > 0) return { type: 'up', value: Math.abs(growth) }
    if (growth < 0) return { type: 'down', value: Math.abs(growth) }
    return { type: 'neutral', value: 0 }
  }

  // Financial metrics
  const calculateRevenue = (items) => {
    return calculateTotal(
      items.filter(item => item.tipo === 'RECEITA'), 
      'valor'
    )
  }

  const calculateExpenses = (items) => {
    return calculateTotal(
      items.filter(item => item.tipo === 'DESPESA'), 
      'valor'
    )
  }

  const calculateBalance = (items) => {
    return calculateRevenue(items) - calculateExpenses(items)
  }

  const calculateEfficiency = (revenue, expenses) => {
    if (!revenue || revenue === 0) return 0
    return ((revenue - expenses) / revenue) * 100
  }

  // Category analysis
  const groupByCategory = (items) => {
    return items.reduce((groups, item) => {
      const category = item.categoria || 'Sem categoria'
      if (!groups[category]) {
        groups[category] = []
      }
      groups[category].push(item)
      return groups
    }, {})
  }

  const calculateCategoryTotals = (items) => {
    const grouped = groupByCategory(items)
    
    return Object.entries(grouped).map(([category, categoryItems]) => ({
      category,
      total: calculateTotal(categoryItems, 'valor'),
      count: categoryItems.length,
      percentage: items.length ? (categoryItems.length / items.length) * 100 : 0
    }))
  }

  // Time-based analysis
  const groupByPeriod = (items, period = 'month') => {
    return items.reduce((groups, item) => {
      if (!item.data_lancamento) return groups
      
      const date = new Date(item.data_lancamento)
      let key
      
      switch (period) {
        case 'day':
          key = date.toISOString().split('T')[0]
          break
        case 'week':
          const weekStart = new Date(date)
          weekStart.setDate(date.getDate() - date.getDay())
          key = weekStart.toISOString().split('T')[0]
          break
        case 'month':
          key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
          break
        case 'year':
          key = String(date.getFullYear())
          break
        default:
          key = date.toISOString().split('T')[0]
      }
      
      if (!groups[key]) {
        groups[key] = []
      }
      groups[key].push(item)
      return groups
    }, {})
  }

  const calculateMonthlyTrends = (items) => {
    const grouped = groupByPeriod(items, 'month')
    
    return Object.entries(grouped)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([month, monthItems]) => ({
        period: month,
        revenue: calculateRevenue(monthItems),
        expenses: calculateExpenses(monthItems),
        balance: calculateBalance(monthItems),
        count: monthItems.length
      }))
  }

  // Computed metrics (reactive to data changes)
  const metrics = computed(() => {
    if (!data.value || !Array.isArray(data.value)) {
      return {
        total: 0,
        revenue: 0,
        expenses: 0,
        balance: 0,
        efficiency: 0,
        count: 0
      }
    }

    const revenue = calculateRevenue(data.value)
    const expenses = calculateExpenses(data.value)
    const balance = calculateBalance(data.value)
    const efficiency = calculateEfficiency(revenue, expenses)

    return {
      total: data.value.length,
      revenue,
      expenses,
      balance,
      efficiency,
      count: data.value.length,
      
      // Formatted versions
      formattedRevenue: formatCurrency(revenue),
      formattedExpenses: formatCurrency(expenses),
      formattedBalance: formatCurrency(balance),
      formattedEfficiency: formatPercentage(efficiency),
      
      // Trends (requires comparison data)
      balanceTrend: balance >= 0 ? 'positive' : 'negative'
    }
  })

  const categoryMetrics = computed(() => {
    if (!data.value || !Array.isArray(data.value)) return []
    return calculateCategoryTotals(data.value)
  })

  const monthlyMetrics = computed(() => {
    if (!data.value || !Array.isArray(data.value)) return []
    return calculateMonthlyTrends(data.value)
  })

  return {
    // Formatters
    formatCurrency,
    formatNumber,
    formatPercentage,
    formatDate,

    // Calculations
    calculateTotal,
    calculateAverage,
    calculateGrowth,
    calculateGrowthTrend,
    calculateRevenue,
    calculateExpenses,
    calculateBalance,
    calculateEfficiency,

    // Analysis
    groupByCategory,
    groupByPeriod,
    calculateCategoryTotals,
    calculateMonthlyTrends,

    // Reactive metrics
    metrics,
    categoryMetrics,
    monthlyMetrics
  }
} 