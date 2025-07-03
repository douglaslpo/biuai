import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDashboardStore = defineStore('dashboard', () => {
  // ==================== STATE ====================
  
  // User Preferences
  const userPreferences = ref({
    theme: 'auto', // 'light', 'dark', 'auto'
    layout: 'default', // 'default', 'compact', 'expanded'
    chartsPeriod: '30d', // '7d', '30d', '90d', '1y'
    currency: 'BRL',
    dateFormat: 'DD/MM/YYYY',
    autoRefresh: true,
    refreshInterval: 600000, // 10 minutes
    showAnimations: true,
    soundEnabled: true,
    compactMode: false
  })

  // Widget Configuration
  const widgetSettings = ref({
    metrics: {
      enabled: true,
      position: 0,
      visible: ['receitas', 'despesas', 'saldo', 'efficiency']
    },
    insights: {
      enabled: true,
      position: 1,
      maxItems: 3
    },
    alerts: {
      enabled: true,
      position: 2,
      types: ['financial', 'system', 'goals']
    },
    charts: {
      enabled: true,
      position: 3,
      layout: 'side-by-side' // 'side-by-side', 'stacked'
    },
    analytics: {
      enabled: true,
      position: 4,
      visible: ['kpis', 'trends', 'goals']
    },
    activity: {
      enabled: true,
      position: 5,
      recentTransactions: 10,
      showSystemMonitoring: true
    }
  })

  // Cache Management
  const cache = ref({
    summary: {
      data: null,
      timestamp: null,
      ttl: 300000 // 5 minutes
    },
    charts: {
      data: null,
      timestamp: null,
      ttl: 900000 // 15 minutes
    },
    insights: {
      data: null,
      timestamp: null,
      ttl: 1800000 // 30 minutes
    },
    transactions: {
      data: null,
      timestamp: null,
      ttl: 60000 // 1 minute
    }
  })

  // Performance Tracking
  const performance = ref({
    loadTimes: {
      initial: null,
      refresh: null,
      navigation: null
    },
    apiResponseTimes: {
      summary: [],
      charts: [],
      transactions: []
    },
    renderTimes: {
      metrics: null,
      charts: null,
      tables: null
    },
    memoryUsage: {
      initial: null,
      current: null,
      peak: null
    },
    errorCount: 0,
    warningCount: 0
  })

  // SIOG Integration
  const siogData = ref({
    lastImport: null,
    importHistory: [],
    mappedCategories: {},
    validationRules: {
      requiredFields: ['data', 'valor', 'descricao'],
      dateFormat: 'DD/MM/YYYY',
      currencyFormat: 'pt-BR'
    },
    processingStatus: 'idle' // 'idle', 'processing', 'success', 'error'
  })

  // Loading States
  const loading = ref({
    dashboard: false,
    export: false,
    import: false,
    preferences: false
  })

  // ==================== GETTERS ====================
  
  const currentTheme = computed(() => {
    if (userPreferences.value.theme === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return userPreferences.value.theme
  })

  const enabledWidgets = computed(() => {
    return Object.entries(widgetSettings.value)
      .filter(([key, widget]) => widget.enabled)
      .sort((a, b) => a[1].position - b[1].position)
      .map(([key]) => key)
  })

  const cacheStatus = computed(() => {
    const now = Date.now()
    const status = {}
    
    Object.entries(cache.value).forEach(([key, cacheData]) => {
      status[key] = {
        valid: cacheData.timestamp && (now - cacheData.timestamp) < cacheData.ttl,
        age: cacheData.timestamp ? now - cacheData.timestamp : null,
        expired: cacheData.timestamp ? (now - cacheData.timestamp) >= cacheData.ttl : true
      }
    })
    
    return status
  })

  const performanceMetrics = computed(() => {
    const { apiResponseTimes } = performance.value
    
    return {
      avgApiResponse: {
        summary: calculateAverage(apiResponseTimes.summary),
        charts: calculateAverage(apiResponseTimes.charts),
        transactions: calculateAverage(apiResponseTimes.transactions)
      },
      totalErrors: performance.value.errorCount,
      totalWarnings: performance.value.warningCount,
      memoryUsage: performance.value.memoryUsage.current || 0
    }
  })

  // ==================== ACTIONS ====================

  // Preferences Management
  const updatePreferences = async (newPreferences) => {
    loading.value.preferences = true
    try {
      userPreferences.value = { ...userPreferences.value, ...newPreferences }
      await persistPreferences()
      return true
    } catch (error) {
      console.error('Error updating preferences:', error)
      return false
    } finally {
      loading.value.preferences = false
    }
  }

  const resetPreferences = async () => {
    const defaultPreferences = {
      theme: 'auto',
      layout: 'default',
      chartsPeriod: '30d',
      currency: 'BRL',
      dateFormat: 'DD/MM/YYYY',
      autoRefresh: true,
      refreshInterval: 600000,
      showAnimations: true,
      soundEnabled: true,
      compactMode: false
    }
    
    await updatePreferences(defaultPreferences)
  }

  // Widget Management
  const updateWidgetSettings = (widgetKey, settings) => {
    if (widgetSettings.value[widgetKey]) {
      widgetSettings.value[widgetKey] = { 
        ...widgetSettings.value[widgetKey], 
        ...settings 
      }
      persistWidgetSettings()
    }
  }

  const toggleWidget = (widgetKey) => {
    if (widgetSettings.value[widgetKey]) {
      widgetSettings.value[widgetKey].enabled = !widgetSettings.value[widgetKey].enabled
      persistWidgetSettings()
    }
  }

  const reorderWidgets = (newOrder) => {
    newOrder.forEach((widgetKey, index) => {
      if (widgetSettings.value[widgetKey]) {
        widgetSettings.value[widgetKey].position = index
      }
    })
    persistWidgetSettings()
  }

  // Cache Management
  const setCacheData = (key, data) => {
    if (cache.value[key]) {
      cache.value[key] = {
        ...cache.value[key],
        data,
        timestamp: Date.now()
      }
    }
  }

  const getCacheData = (key) => {
    const cacheData = cache.value[key]
    if (!cacheData || !cacheData.timestamp) return null
    
    const now = Date.now()
    const isValid = (now - cacheData.timestamp) < cacheData.ttl
    
    return isValid ? cacheData.data : null
  }

  const clearCache = (key = null) => {
    if (key && cache.value[key]) {
      cache.value[key] = {
        ...cache.value[key],
        data: null,
        timestamp: null
      }
    } else {
      Object.keys(cache.value).forEach(cacheKey => {
        cache.value[cacheKey] = {
          ...cache.value[cacheKey],
          data: null,
          timestamp: null
        }
      })
    }
  }

  // Performance Tracking
  const trackLoadTime = (type, duration) => {
    performance.value.loadTimes[type] = duration
  }

  const trackApiResponse = (endpoint, duration) => {
    const responseArray = performance.value.apiResponseTimes[endpoint]
    if (responseArray) {
      responseArray.push(duration)
      // Keep only last 100 measurements
      if (responseArray.length > 100) {
        responseArray.splice(0, responseArray.length - 100)
      }
    }
  }

  const trackRenderTime = (component, duration) => {
    performance.value.renderTimes[component] = duration
  }

  const trackError = () => {
    performance.value.errorCount++
  }

  const trackWarning = () => {
    performance.value.warningCount++
  }

  const updateMemoryUsage = () => {
    if ('memory' in performance) {
      const memInfo = performance.memory
      performance.value.memoryUsage = {
        ...performance.value.memoryUsage,
        current: memInfo.usedJSHeapSize,
        peak: Math.max(performance.value.memoryUsage.peak || 0, memInfo.usedJSHeapSize)
      }
    }
  }

  // SIOG Integration
  const importSiogData = async (file) => {
    loading.value.import = true
    siogData.value.processingStatus = 'processing'
    
    try {
      const data = await processSiogFile(file)
      const validatedData = await validateSiogData(data)
      const mappedData = await mapSiogCategories(validatedData)
      
      // Store import history
      siogData.value.importHistory.unshift({
        timestamp: new Date().toISOString(),
        recordCount: mappedData.length,
        status: 'success'
      })
      
      siogData.value.lastImport = new Date().toISOString()
      siogData.value.processingStatus = 'success'
      
      // Clear cache to force refresh
      clearCache()
      
      return mappedData
    } catch (error) {
      siogData.value.processingStatus = 'error'
      siogData.value.importHistory.unshift({
        timestamp: new Date().toISOString(),
        error: error.message,
        status: 'error'
      })
      throw error
    } finally {
      loading.value.import = false
    }
  }

  const exportData = async (options = {}) => {
    loading.value.export = true
    
    try {
      const {
        format = 'xlsx',
        dateRange = '30d',
        includeCategories = true,
        includeGoals = true,
        includeAccounts = true
      } = options

      const exportData = await generateExportData({
        format,
        dateRange,
        includeCategories,
        includeGoals,
        includeAccounts
      })

      const filename = `biuai-export-${new Date().toISOString().split('T')[0]}.${format}`
      downloadFile(exportData, filename, format)
      
      return true
    } catch (error) {
      console.error('Export error:', error)
      throw error
    } finally {
      loading.value.export = false
    }
  }

  // ==================== HELPER FUNCTIONS ====================

  const calculateAverage = (arr) => {
    if (!arr || arr.length === 0) return 0
    return arr.reduce((sum, val) => sum + val, 0) / arr.length
  }

  const persistPreferences = async () => {
    localStorage.setItem('biuai-dashboard-preferences', JSON.stringify(userPreferences.value))
  }

  const persistWidgetSettings = async () => {
    localStorage.setItem('biuai-widget-settings', JSON.stringify(widgetSettings.value))
  }

  const loadPreferences = () => {
    const saved = localStorage.getItem('biuai-dashboard-preferences')
    if (saved) {
      userPreferences.value = { ...userPreferences.value, ...JSON.parse(saved) }
    }
  }

  const loadWidgetSettings = () => {
    const saved = localStorage.getItem('biuai-widget-settings')
    if (saved) {
      widgetSettings.value = { ...widgetSettings.value, ...JSON.parse(saved) }
    }
  }

  const processSiogFile = async (file) => {
    // Implementation for processing SIOG files
    // This would handle CSV/Excel parsing
    return []
  }

  const validateSiogData = async (data) => {
    // Implementation for validating SIOG data structure
    return data
  }

  const mapSiogCategories = async (data) => {
    // Implementation for mapping SIOG categories to BIUAI categories
    return data
  }

  const generateExportData = async (options) => {
    // Implementation for generating export data
    return new Blob([''], { type: 'application/octet-stream' })
  }

  const downloadFile = (data, filename, format) => {
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // Initialize
  const initialize = () => {
    loadPreferences()
    loadWidgetSettings()
    
    if (performance.value.memoryUsage.initial === null) {
      updateMemoryUsage()
      performance.value.memoryUsage.initial = performance.value.memoryUsage.current
    }
  }

  // Auto-initialize
  initialize()

  // ==================== RETURN ====================
  
  return {
    // State
    userPreferences,
    widgetSettings,
    cache,
    performance,
    siogData,
    loading,
    
    // Getters
    currentTheme,
    enabledWidgets,
    cacheStatus,
    performanceMetrics,
    
    // Actions
    updatePreferences,
    resetPreferences,
    updateWidgetSettings,
    toggleWidget,
    reorderWidgets,
    setCacheData,
    getCacheData,
    clearCache,
    trackLoadTime,
    trackApiResponse,
    trackRenderTime,
    trackError,
    trackWarning,
    updateMemoryUsage,
    importSiogData,
    exportData,
    initialize
  }
}) 