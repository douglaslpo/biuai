<template>
  <BaseCard
    :title="title"
    :subtitle="subtitle"
    :icon="icon"
    :type="status"
    :loading="loading"
    class="biuai-mcp-widget"
    hover
  >
    <template #title v-if="!title">
      <div class="d-flex align-center justify-space-between">
        <div class="d-flex align-center">
          <v-icon :icon="icon" :color="statusColor" class="me-3" size="large" />
          <div>
            <h3 class="text-h6 font-weight-bold">{{ displayTitle }}</h3>
            <p class="text-caption text-medium-emphasis mb-0">
              {{ displaySubtitle }}
            </p>
          </div>
        </div>
        <v-chip
          :color="statusColor"
          size="small"
          variant="flat"
        >
          {{ statusText }}
        </v-chip>
      </div>
    </template>

    <!-- Métricas principais -->
    <div v-if="metrics && metrics.length > 0" class="mb-4">
      <v-row>
        <v-col
          v-for="metric in metrics"
          :key="metric.name"
          cols="6"
        >
          <div class="text-center">
            <div class="text-h4 font-weight-bold" :class="`text-${metric.color || statusColor}`">
              {{ formatValue(metric.value, metric.format) }}
            </div>
            <div class="text-caption text-medium-emphasis">
              {{ metric.label }}
            </div>
          </div>
        </v-col>
      </v-row>
    </div>

    <!-- Lista de itens -->
    <div v-if="items && items.length > 0" class="biuai-mcp-items">
      <v-list density="compact" class="pa-0">
        <v-list-item
          v-for="(item, index) in displayItems"
          :key="index"
          class="px-2"
        >
          <template #prepend>
            <v-icon
              :icon="item.icon || 'mdi-circle-small'"
              :color="item.color || 'grey'"
              size="small"
            />
          </template>
          
          <v-list-item-title class="text-body-2">
            {{ item.title }}
          </v-list-item-title>
          
          <v-list-item-subtitle v-if="item.subtitle" class="text-caption">
            {{ item.subtitle }}
          </v-list-item-subtitle>
          
          <template #append v-if="item.value">
            <v-chip
              size="x-small"
              :color="item.valueColor || 'grey'"
              variant="tonal"
            >
              {{ formatValue(item.value, item.valueFormat) }}
            </v-chip>
          </template>
        </v-list-item>
      </v-list>
      
      <!-- Ver mais -->
      <div v-if="items.length > maxItems" class="text-center mt-2">
        <v-btn
          variant="text"
          size="small"
          color="primary"
          @click="toggleShowAll"
        >
          {{ showAll ? 'Ver menos' : `Ver mais (${items.length - maxItems})` }}
          <v-icon :icon="showAll ? 'mdi-chevron-up' : 'mdi-chevron-down'" end />
        </v-btn>
      </div>
    </div>

    <!-- Gráfico simples -->
    <div v-if="chartData" class="biuai-mcp-chart mt-4">
      <canvas ref="chartCanvas" height="100"></canvas>
    </div>

    <!-- Mensagem vazia -->
    <div v-if="isEmpty" class="text-center py-6">
      <v-icon icon="mdi-information-outline" size="48" color="grey" class="mb-2" />
      <p class="text-body-2 text-medium-emphasis">
        {{ emptyMessage || 'Nenhum dado disponível' }}
      </p>
    </div>

    <template #actions>
      <v-spacer />
      <BaseButton
        v-if="refreshable"
        icon="mdi-refresh"
        variant="text"
        size="small"
        :loading="loading"
        @click="handleRefresh"
      />
      <BaseButton
        v-if="actionButton"
        :text="actionButton.text"
        :icon="actionButton.icon"
        :variant="actionButton.variant || 'outlined'"
        :color="actionButton.color || 'primary'"
        size="small"
        @click="handleAction"
      />
    </template>
  </BaseCard>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, nextTick } from 'vue'
import BaseCard from './base/BaseCard.vue'
import BaseButton from './base/BaseButton.vue'

const props = defineProps({
  // Informações básicas
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: 'mdi-monitor-dashboard'
  },

  // Tipo de widget
  type: {
    type: String,
    default: 'status',
    validator: (value) => ['status', 'metrics', 'list', 'chart', 'alerts'].includes(value)
  },

  // Status
  status: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'warning', 'error', 'info', 'default'].includes(value)
  },

  // Dados
  metrics: {
    type: Array,
    default: () => []
  },
  items: {
    type: Array,
    default: () => []
  },
  chartData: {
    type: Object,
    default: null
  },

  // Configurações
  maxItems: {
    type: Number,
    default: 3
  },
  refreshable: {
    type: Boolean,
    default: true
  },
  autoRefresh: {
    type: Number,
    default: 0 // segundos, 0 = desabilitado
  },
  actionButton: {
    type: Object,
    default: null
  },
  emptyMessage: {
    type: String,
    default: ''
  },

  // Estados
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['refresh', 'action'])

const showAll = ref(false)
const chartCanvas = ref(null)
const refreshInterval = ref(null)

const displayTitle = computed(() => {
  if (props.title) return props.title
  
  const typeLabels = {
    status: 'Status do Sistema',
    metrics: 'Métricas',
    list: 'Lista de Itens',
    chart: 'Gráfico',
    alerts: 'Alertas'
  }
  
  return typeLabels[props.type] || 'MCP Widget'
})

const displaySubtitle = computed(() => {
  if (props.subtitle) return props.subtitle
  
  return 'Monitoramento em tempo real'
})

const statusColor = computed(() => {
  const colorMap = {
    success: 'success',
    warning: 'warning',
    error: 'error',
    info: 'info',
    default: 'grey'
  }
  
  return colorMap[props.status] || 'info'
})

const statusText = computed(() => {
  const textMap = {
    success: 'Online',
    warning: 'Atenção',
    error: 'Erro',
    info: 'Info',
    default: 'Normal'
  }
  
  return textMap[props.status] || 'Normal'
})

const displayItems = computed(() => {
  if (!props.items) return []
  
  if (showAll.value || props.items.length <= props.maxItems) {
    return props.items
  }
  
  return props.items.slice(0, props.maxItems)
})

const isEmpty = computed(() => {
  return !props.metrics?.length && !props.items?.length && !props.chartData
})

const formatValue = (value, format) => {
  if (!format) return value
  
  switch (format) {
    case 'currency':
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      }).format(value)
    case 'number':
      return new Intl.NumberFormat('pt-BR').format(value)
    case 'percentage':
      return `${value}%`
    case 'bytes':
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      if (value === 0) return '0 B'
      const i = Math.floor(Math.log(value) / Math.log(1024))
      return `${(value / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
    default:
      return value
  }
}

const toggleShowAll = () => {
  showAll.value = !showAll.value
}

const handleRefresh = () => {
  emit('refresh')
}

const handleAction = () => {
  emit('action')
}

const setupAutoRefresh = () => {
  if (props.autoRefresh > 0) {
    refreshInterval.value = setInterval(() => {
      if (!props.loading) {
        handleRefresh()
      }
    }, props.autoRefresh * 1000)
  }
}

const clearAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

const initChart = async () => {
  if (!props.chartData || !chartCanvas.value) return
  
  await nextTick()
  
  // Implementação básica de gráfico com Canvas API
  const canvas = chartCanvas.value
  const ctx = canvas.getContext('2d')
  const { data, labels } = props.chartData
  
  // Limpar canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  if (!data || !data.length) return
  
  const padding = 20
  const width = canvas.width - padding * 2
  const height = canvas.height - padding * 2
  
  const max = Math.max(...data)
  const min = Math.min(...data)
  const range = max - min || 1
  
  // Desenhar linha
  ctx.strokeStyle = '#1976D2'
  ctx.lineWidth = 2
  ctx.beginPath()
  
  data.forEach((value, index) => {
    const x = padding + (index / (data.length - 1)) * width
    const y = padding + ((max - value) / range) * height
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  
  ctx.stroke()
  
  // Desenhar pontos
  ctx.fillStyle = '#1976D2'
  data.forEach((value, index) => {
    const x = padding + (index / (data.length - 1)) * width
    const y = padding + ((max - value) / range) * height
    
    ctx.beginPath()
    ctx.arc(x, y, 3, 0, 2 * Math.PI)
    ctx.fill()
  })
}

onMounted(() => {
  setupAutoRefresh()
  initChart()
})

onUnmounted(() => {
  clearAutoRefresh()
})
</script>

<style lang="scss" scoped>
.biuai-mcp-widget {
  :deep(.biuai-card-title) {
    padding-bottom: 8px;
  }
}

.biuai-mcp-items {
  max-height: 200px;
  overflow-y: auto;
}

.biuai-mcp-chart {
  canvas {
    width: 100%;
    max-height: 100px;
  }
}
</style> 