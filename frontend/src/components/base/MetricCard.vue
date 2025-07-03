<template>
  <v-card 
    :class="cardClasses"
    :elevation="elevation"
    :hover="hover"
    @click="handleClick"
  >
    <v-card-text class="pa-6">
      <div class="metric-content">
        <!-- Icon -->
        <div v-if="icon" class="metric-icon-wrapper mb-3">
          <v-icon 
            :icon="icon" 
            :size="iconSize" 
            :class="iconClasses"
          />
        </div>
        
        <!-- Value and Label -->
        <div class="metric-info">
          <div class="metric-label">{{ label }}</div>
          <div class="metric-value">
            <CountUp
              v-if="animated && typeof value === 'number'"
              :endVal="value"
              :options="countUpOptions"
            />
            <span v-else>{{ formattedValue }}</span>
          </div>
          <div v-if="subtitle" class="metric-subtitle">
            {{ subtitle }}
          </div>
        </div>
        
        <!-- Trend indicator -->
        <div v-if="trend" class="metric-trend mt-2">
          <v-chip
            :color="trendColor"
            size="small"
            variant="tonal"
          >
            <v-icon 
              :icon="trendIcon" 
              size="small" 
              class="mr-1"
            />
            {{ trend.value }}{{ trend.unit || '%' }}
          </v-chip>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import CountUp from 'vue-countup-v3'

// Props
const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  iconSize: {
    type: [String, Number],
    default: 32
  },
  color: {
    type: String,
    default: 'primary'
  },
  elevation: {
    type: [String, Number],
    default: 8
  },
  hover: {
    type: Boolean,
    default: true
  },
  clickable: {
    type: Boolean,
    default: false
  },
  animated: {
    type: Boolean,
    default: true
  },
  format: {
    type: String,
    default: 'number' // 'number', 'currency', 'percentage'
  },
  trend: {
    type: Object,
    default: null
    // { value: 12, type: 'up', unit: '%' }
  }
})

// Emits
const emit = defineEmits(['click'])

// Computed
const cardClasses = computed(() => [
  'metric-card',
  `metric-card--${props.color}`,
  {
    'metric-card--clickable': props.clickable
  }
])

const iconClasses = computed(() => [
  'metric-icon',
  `text-${props.color}`
])

const formattedValue = computed(() => {
  if (typeof props.value === 'string') return props.value
  
  switch (props.format) {
    case 'currency':
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      }).format(props.value)
    
    case 'percentage':
      return `${props.value}%`
    
    default:
      return new Intl.NumberFormat('pt-BR').format(props.value)
  }
})

const trendColor = computed(() => {
  if (!props.trend) return 'primary'
  
  switch (props.trend.type) {
    case 'up': return 'success'
    case 'down': return 'error'
    default: return 'info'
  }
})

const trendIcon = computed(() => {
  if (!props.trend) return 'mdi-trending-neutral'
  
  switch (props.trend.type) {
    case 'up': return 'mdi-trending-up'
    case 'down': return 'mdi-trending-down'
    default: return 'mdi-trending-neutral'
  }
})

const countUpOptions = computed(() => ({
  duration: 2,
  useGrouping: true,
  separator: '.',
  decimal: ',',
  prefix: props.format === 'currency' ? 'R$ ' : '',
  suffix: props.format === 'percentage' ? '%' : ''
}))

// Methods
const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped>
.metric-card {
  position: relative;
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(var(--v-theme-surface), 0.12);
}

.metric-card--clickable {
  cursor: pointer;
}

.metric-card--clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.metric-content {
  position: relative;
}

.metric-icon-wrapper {
  display: inline-flex;
  padding: 12px;
  border-radius: 12px;
  background: rgba(var(--v-theme-primary), 0.1);
}

.metric-icon {
  opacity: 0.9;
}

.metric-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(var(--v-theme-on-surface), 0.7);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: rgb(var(--v-theme-on-surface));
  line-height: 1.2;
  margin-bottom: 4px;
}

.metric-subtitle {
  font-size: 0.75rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
}

.metric-trend {
  position: absolute;
  top: 16px;
  right: 16px;
}

/* Color variants */
.metric-card--primary .metric-icon-wrapper {
  background: rgba(var(--v-theme-primary), 0.1);
}

.metric-card--success .metric-icon-wrapper {
  background: rgba(var(--v-theme-success), 0.1);
}

.metric-card--error .metric-icon-wrapper {
  background: rgba(var(--v-theme-error), 0.1);
}

.metric-card--warning .metric-icon-wrapper {
  background: rgba(var(--v-theme-warning), 0.1);
}

.metric-card--info .metric-icon-wrapper {
  background: rgba(var(--v-theme-info), 0.1);
}

/* Responsividade */
@media (max-width: 768px) {
  .metric-value {
    font-size: 1.75rem;
  }
  
  .metric-trend {
    position: relative;
    top: auto;
    right: auto;
    margin-top: 8px;
  }
}

@media (max-width: 480px) {
  .metric-value {
    font-size: 1.5rem;
  }
}
</style> 