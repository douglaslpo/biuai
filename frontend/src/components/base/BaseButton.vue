<template>
  <v-btn
    :class="buttonClass"
    :variant="computedVariant"
    :color="computedColor"
    :size="size"
    :rounded="rounded"
    :loading="loading"
    :disabled="disabled"
    :block="block"
    :icon="isIconOnly"
    v-bind="$attrs"
    @click="handleClick"
  >
    <!-- Ícone inicial -->
    <v-icon
      v-if="prependIcon && !isIconOnly"
      :icon="prependIcon"
      start
    />
    
    <!-- Ícone único (para botão de ícone) -->
    <v-icon
      v-if="isIconOnly"
      :icon="icon"
    />
    
    <!-- Texto do botão -->
    <span v-if="!isIconOnly">
      <slot>{{ text }}</slot>
    </span>
    
    <!-- Ícone final -->
    <v-icon
      v-if="appendIcon && !isIconOnly"
      :icon="appendIcon"
      end
    />
  </v-btn>
</template>

<script setup>
import { computed } from 'vue'

defineOptions({
  inheritAttrs: false
})

const props = defineProps({
  // Conteúdo
  text: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  prependIcon: {
    type: String,
    default: ''
  },
  appendIcon: {
    type: String,
    default: ''
  },

  // Aparência
  variant: {
    type: String,
    default: 'elevated',
    validator: (value) => ['flat', 'elevated', 'tonal', 'outlined', 'text', 'plain'].includes(value)
  },
  color: {
    type: String,
    default: 'primary'
  },
  size: {
    type: String,
    default: 'default',
    validator: (value) => ['x-small', 'small', 'default', 'large', 'x-large'].includes(value)
  },
  rounded: {
    type: [String, Number, Boolean],
    default: 'lg'
  },

  // Tipo especial do BIUAI
  type: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'success', 'error', 'warning', 'info', 'neutral'].includes(value)
  },

  // Estados
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  block: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const isIconOnly = computed(() => {
  return props.icon && !props.text && !props.$slots.default
})

const buttonClass = computed(() => {
  const classes = ['biuai-btn']
  
  if (props.type !== 'primary') {
    classes.push(`biuai-btn--${props.type}`)
  }
  
  return classes
})

const computedVariant = computed(() => {
  // Mapear tipos especiais para variantes do Vuetify se necessário
  if (props.type === 'neutral' && props.variant === 'elevated') {
    return 'outlined'
  }
  
  return props.variant
})

const computedColor = computed(() => {
  // Mapear tipos para cores do tema
  const typeColorMap = {
    primary: 'primary',
    secondary: 'secondary',
    success: 'success',
    error: 'error',
    warning: 'warning',
    info: 'info',
    neutral: 'surface-variant'
  }
  
  return props.color !== 'primary' ? props.color : typeColorMap[props.type] || 'primary'
})

const handleClick = (event) => {
  if (!props.loading && !props.disabled) {
    emit('click', event)
  }
}
</script>

<style lang="scss" scoped>
.biuai-btn {
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.02em;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
  }
  
  &--secondary {
    &.v-btn--variant-elevated {
      background: rgb(var(--v-theme-secondary)) !important;
      color: rgb(var(--v-theme-on-secondary)) !important;
    }
  }
  
  &--success {
    &.v-btn--variant-elevated {
      background: rgb(var(--v-theme-success)) !important;
      color: rgb(var(--v-theme-on-success)) !important;
    }
  }
  
  &--error {
    &.v-btn--variant-elevated {
      background: rgb(var(--v-theme-error)) !important;
      color: rgb(var(--v-theme-on-error)) !important;
    }
  }
  
  &--warning {
    &.v-btn--variant-elevated {
      background: rgb(var(--v-theme-warning)) !important;
      color: rgb(var(--v-theme-on-warning)) !important;
    }
  }
  
  &--info {
    &.v-btn--variant-elevated {
      background: rgb(var(--v-theme-info)) !important;
      color: rgb(var(--v-theme-on-info)) !important;
    }
  }
  
  &--neutral {
    &.v-btn--variant-outlined {
      border-color: rgba(var(--v-theme-on-surface), 0.12);
      color: rgb(var(--v-theme-on-surface));
      
      &:hover {
        background: rgba(var(--v-theme-on-surface), 0.04);
      }
    }
  }
}
</style> 