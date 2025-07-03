<template>
  <v-row class="metrics-grid" no-gutters>
    <v-col
      v-for="(metric, index) in metricsData"
      :key="metric.key"
      cols="12"
      sm="6"
      lg="3"
      class="pa-2"
    >
      <v-card
        :class="[
          'metric-card',
          `metric-card--${metric.type}`,
          { 'metric-card--loading': loading }
        ]"
        :elevation="metric.elevated ? 12 : 6"
        :style="{ animationDelay: `${index * 150}ms` }"
        hover
      >
        <v-card-text class="pa-6">
          <div class="metric-header d-flex align-center justify-space-between mb-4">
            <div class="metric-icon-container">
              <v-avatar
                :color="metric.iconBg"
                size="56"
                class="metric-avatar elevation-4"
              >
                <v-icon 
                  :icon="metric.icon" 
                  size="28"
                  :color="metric.iconColor"
                  class="metric-icon"
                />
              </v-avatar>
            </div>
            
            <div class="metric-trend">
              <v-chip
                :color="metric.trendColor"
                :prepend-icon="metric.trendIcon"
                size="small"
                variant="flat"
                class="metric-trend-chip"
              >
                {{ metric.trendText }}
              </v-chip>
            </div>
          </div>

          <div class="metric-content">
            <h3 class="metric-label text-body-2 font-weight-medium mb-2">
              {{ metric.label }}
            </h3>
            
            <div class="metric-value-container">
              <h2 class="metric-value text-h4 font-weight-bold mb-1">
                <v-skeleton-loader
                  v-if="loading"
                  type="text"
                  width="120"
                  height="32"
                />
                <CountUp
                  v-else
                  :end-val="metric.value"
                  :options="countUpOptions"
                  :prefix="metric.prefix"
                  :suffix="metric.suffix"
                  :formatter="metric.formatter"
                />
              </h2>
              
              <p class="metric-subtitle text-body-2 text-medium-emphasis mb-3">
                {{ metric.subtitle }}
              </p>
            </div>

            <!-- Progress Indicator -->
            <div v-if="metric.progress !== undefined" class="metric-progress mb-3">
              <div class="d-flex justify-space-between align-center mb-1">
                <span class="text-caption">Progresso</span>
                <span class="text-caption font-weight-medium">{{ metric.progress }}%</span>
              </div>
              <v-progress-linear
                :model-value="metric.progress"
                :color="metric.progressColor"
                height="6"
                rounded
                class="metric-progress-bar"
              />
            </div>

            <!-- Quick Actions -->
            <div v-if="metric.actions && metric.actions.length" class="metric-actions">
              <v-btn
                v-for="action in metric.actions"
                :key="action.key"
                :color="action.color"
                :variant="action.variant || 'text'"
                :size="action.size || 'small'"
                :prepend-icon="action.icon"
                @click="handleAction(action)"
                class="metric-action-btn"
              >
                {{ action.label }}
              </v-btn>
            </div>
          </div>
        </v-card-text>

        <!-- Card Overlay for loading state -->
        <v-overlay
          v-if="loading"
          contained
          class="align-center justify-center"
        >
          <v-progress-circular indeterminate color="primary" />
        </v-overlay>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { computed, ref } from 'vue'
import CountUp from 'vue-countup-v3'

// Props
const props = defineProps({
  summary: {
    type: Object,
    default: () => ({})
  },
  loading: {
    type: Boolean,
    default: false
  },
  trendData: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['action'])

// Computed metrics data
const metricsData = computed(() => {
  const { summary } = props
  
  return [
    // Receitas Card
    {
      key: 'receitas',
      type: 'success',
      label: 'Receitas',
      value: Math.abs(summary.total_receitas || 0),
      prefix: 'R$ ',
      formatter: formatCurrency,
      subtitle: `${summary.total_receitas_count || 0} lançamentos • ${summary.periodo_dias || 30} dias`,
      icon: 'mdi-trending-up',
      iconBg: 'rgba(76, 175, 80, 0.1)',
      iconColor: 'success',
      trendText: getTrendText(summary.crescimento_receitas || 0),
      trendIcon: getTrendIcon(summary.crescimento_receitas || 0),
      trendColor: getTrendColor(summary.crescimento_receitas || 0),
      progress: calculateProgress(summary.total_receitas, 30000), // Meta de R$ 30k
      progressColor: 'success',
      elevated: (summary.crescimento_receitas || 0) > 10,
      actions: [
        {
          key: 'new-receita',
          label: 'Adicionar',
          icon: 'mdi-plus',
          color: 'success',
          variant: 'tonal'
        }
      ]
    },

    // Despesas Card  
    {
      key: 'despesas',
      type: 'error',
      label: 'Despesas',
      value: Math.abs(summary.total_despesas || 0),
      prefix: 'R$ ',
      formatter: formatCurrency,
      subtitle: `${summary.total_despesas_count || 0} lançamentos • ${summary.periodo_dias || 30} dias`,
      icon: 'mdi-trending-down',
      iconBg: 'rgba(244, 67, 54, 0.1)',
      iconColor: 'error',
      trendText: getTrendText(summary.crescimento_despesas || 0, true),
      trendIcon: getTrendIcon(summary.crescimento_despesas || 0, true),
      trendColor: getTrendColor(summary.crescimento_despesas || 0, true),
      progress: calculateProgress(Math.abs(summary.total_despesas), 20000), // Meta de controle R$ 20k
      progressColor: 'error',
      elevated: Math.abs(summary.crescimento_despesas || 0) > 10,
      actions: [
        {
          key: 'view-categories',
          label: 'Categorias',
          icon: 'mdi-tag-multiple',
          color: 'error',
          variant: 'text'
        }
      ]
    },

    // Saldo Card - Redesenhado com melhor contraste
    {
      key: 'saldo',
      type: summary.saldo >= 0 ? 'primary' : 'warning',
      label: 'Saldo Total',
      value: Math.abs(summary.saldo || 0),
      prefix: summary.saldo >= 0 ? 'R$ +' : 'R$ -',
      formatter: formatCurrency,
      subtitle: `${summary.total_lancamentos || 0} lançamentos • ${getBalanceStatus(summary.saldo)}`,
      icon: summary.saldo >= 0 ? 'mdi-wallet' : 'mdi-alert-circle',
      iconBg: summary.saldo >= 0 ? 'rgba(33, 150, 243, 0.15)' : 'rgba(255, 152, 0, 0.15)',
      iconColor: summary.saldo >= 0 ? 'primary' : 'warning',
      trendText: getBalanceTrend(summary.saldo),
      trendIcon: summary.saldo >= 0 ? 'mdi-check-circle' : 'mdi-alert',
      trendColor: summary.saldo >= 0 ? 'success' : 'warning',
      progress: summary.saldo >= 0 ? calculateSavingsProgress(summary.saldo) : undefined,
      progressColor: summary.saldo >= 0 ? 'primary' : 'warning',
      elevated: Math.abs(summary.saldo || 0) > 10000,
      actions: [
        {
          key: 'view-goals',
          label: 'Metas',
          icon: 'mdi-target',
          color: 'primary',
          variant: 'tonal'
        }
      ]
    },

    // Eficiência Card - Novo
    {
      key: 'efficiency',
      type: 'info',
      label: 'Eficiência',
      value: calculateEfficiency(summary.total_receitas, summary.total_despesas),
      suffix: '%',
      formatter: (value) => value.toFixed(1),
      subtitle: `Taxa de economia • ${getEfficiencyLabel(calculateEfficiency(summary.total_receitas, summary.total_despesas))}`,
      icon: 'mdi-speedometer',
      iconBg: 'rgba(156, 39, 176, 0.1)',
      iconColor: 'info',
      trendText: getEfficiencyTrend(calculateEfficiency(summary.total_receitas, summary.total_despesas)),
      trendIcon: 'mdi-chart-line',
      trendColor: 'info',
      progress: calculateEfficiency(summary.total_receitas, summary.total_despesas),
      progressColor: 'info',
      elevated: calculateEfficiency(summary.total_receitas, summary.total_despesas) > 70,
      actions: [
        {
          key: 'analytics',
          label: 'Análise',
          icon: 'mdi-chart-arc',
          color: 'info',
          variant: 'text'
        }
      ]
    }
  ]
})

// Count-up animation options
const countUpOptions = {
  duration: 2,
  useEasing: true,
  useGrouping: true,
  separator: '.',
  decimal: ','
}

// Methods
const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value || 0)
}

const getTrendText = (value, inverse = false) => {
  const absValue = Math.abs(value)
  if (absValue < 1) return 'Estável'
  
  const isPositive = inverse ? value < 0 : value > 0
  return `${isPositive ? '+' : ''}${value.toFixed(1)}%`
}

const getTrendIcon = (value, inverse = false) => {
  if (Math.abs(value) < 1) return 'mdi-minus'
  
  const isPositive = inverse ? value < 0 : value > 0
  return isPositive ? 'mdi-trending-up' : 'mdi-trending-down'
}

const getTrendColor = (value, inverse = false) => {
  if (Math.abs(value) < 1) return 'grey'
  
  const isPositive = inverse ? value < 0 : value > 0
  return isPositive ? 'success' : 'error'
}

const getBalanceStatus = (saldo) => {
  if (saldo > 10000) return 'Excelente'
  if (saldo > 5000) return 'Bom'
  if (saldo > 0) return 'Positivo'
  if (saldo > -5000) return 'Atenção'
  return 'Crítico'
}

const getBalanceTrend = (saldo) => {
  if (saldo > 10000) return 'Ótimo!'
  if (saldo > 0) return 'Positivo'
  return 'Atenção'
}

const calculateProgress = (current, target) => {
  if (!target || target <= 0) return 0
  return Math.min(100, (Math.abs(current) / target) * 100)
}

const calculateSavingsProgress = (saldo) => {
  const target = 50000 // Meta de R$ 50k de reserva
  return Math.min(100, (Math.abs(saldo) / target) * 100)
}

const calculateEfficiency = (receitas, despesas) => {
  const receitasAbs = Math.abs(receitas || 0)
  const despesasAbs = Math.abs(despesas || 0)
  
  if (receitasAbs === 0) return 0
  
  const efficiency = ((receitasAbs - despesasAbs) / receitasAbs) * 100
  return Math.max(0, Math.min(100, efficiency))
}

const getEfficiencyLabel = (efficiency) => {
  if (efficiency >= 80) return 'Excelente'
  if (efficiency >= 60) return 'Boa'
  if (efficiency >= 40) return 'Regular'
  if (efficiency >= 20) return 'Baixa'
  return 'Crítica'
}

const getEfficiencyTrend = (efficiency) => {
  if (efficiency >= 70) return 'Ótima'
  if (efficiency >= 50) return 'Boa'
  if (efficiency >= 30) return 'Regular'
  return 'Baixa'
}

const handleAction = (action) => {
  emit('action', action)
}
</script>

<style lang="scss" scoped>
.metrics-grid {
  margin: -8px;
  
  .v-col {
    transition: transform 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
    }
  }
}

.metric-card {
  height: 100%;
  border-radius: 16px;
  border: 1px solid rgba(var(--v-border-color), 0.12);
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85));
  backdrop-filter: blur(10px);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  animation: slideInUp 0.6s ease-out both;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, transparent, rgba(var(--v-theme-primary), 0.5), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    border-color: rgba(var(--v-theme-primary), 0.3);
    
    &::before {
      opacity: 1;
    }
    
    .metric-avatar {
      transform: scale(1.05);
    }
    
    .metric-icon {
      transform: rotate(5deg);
    }
  }
  
  &--success {
    border-left: 4px solid rgb(var(--v-theme-success));
    
    &:hover {
      border-color: rgba(var(--v-theme-success), 0.3);
    }
  }
  
  &--error {
    border-left: 4px solid rgb(var(--v-theme-error));
    
    &:hover {
      border-color: rgba(var(--v-theme-error), 0.3);
    }
  }
  
  &--primary {
    border-left: 4px solid rgb(var(--v-theme-primary));
    
    &:hover {
      border-color: rgba(var(--v-theme-primary), 0.3);
    }
  }
  
  &--warning {
    border-left: 4px solid rgb(var(--v-theme-warning));
    
    &:hover {
      border-color: rgba(var(--v-theme-warning), 0.3);
    }
  }
  
  &--info {
    border-left: 4px solid rgb(var(--v-theme-info));
    
    &:hover {
      border-color: rgba(var(--v-theme-info), 0.3);
    }
  }
  
  &--loading {
    opacity: 0.7;
    pointer-events: none;
  }
}

.metric-header {
  .metric-avatar {
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    
    .metric-icon {
      transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
      opacity: 1 !important; // Fix para ícones apagados
      color: inherit !important;
    }
  }
  
  .metric-trend-chip {
    font-weight: 600;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
  }
}

.metric-content {
  .metric-label {
    color: rgba(var(--v-theme-on-surface), 0.8);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  .metric-value {
    color: rgb(var(--v-theme-on-surface));
    line-height: 1.2;
    font-weight: 700;
  }
  
  .metric-subtitle {
    color: rgba(var(--v-theme-on-surface), 0.6);
    font-size: 0.8rem;
    line-height: 1.4;
  }
}

.metric-progress {
  .metric-progress-bar {
    border-radius: 4px;
    overflow: hidden;
    
    :deep(.v-progress-linear__background) {
      background: rgba(var(--v-theme-surface-variant), 0.3);
    }
  }
}

.metric-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  
  .metric-action-btn {
    font-size: 0.75rem;
    letter-spacing: 0.3px;
    min-height: 28px;
    padding: 0 12px;
    
    :deep(.v-btn__content) {
      font-weight: 600;
    }
  }
}

// Animations
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// Dark theme adjustments
.v-theme--dark {
  .metric-card {
    background: linear-gradient(145deg, rgba(var(--v-theme-surface), 0.95), rgba(var(--v-theme-surface), 0.85));
    border-color: rgba(var(--v-border-color), 0.2);
    
    &:hover {
      background: linear-gradient(145deg, rgba(var(--v-theme-surface), 1), rgba(var(--v-theme-surface), 0.9));
    }
  }
  
  .metric-icon {
    opacity: 1 !important;
  }
}

// Responsive adjustments
@media (max-width: 960px) {
  .metric-card {
    .metric-header {
      margin-bottom: 1rem;
    }
    
    .metric-avatar {
      width: 48px !important;
      height: 48px !important;
      
      .metric-icon {
        font-size: 24px !important;
      }
    }
    
    .metric-value {
      font-size: 1.5rem !important;
    }
  }
}

@media (max-width: 600px) {
  .metrics-grid {
    margin: -4px;
  }
  
  .metric-card {
    .v-card-text {
      padding: 1rem !important;
    }
    
    .metric-actions {
      justify-content: center;
      
      .metric-action-btn {
        flex: 1;
        min-width: 80px;
      }
    }
  }
}
</style> 