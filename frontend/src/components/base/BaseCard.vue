<template>
  <v-card
    :class="cardClass"
    :elevation="computedElevation"
    :variant="variant"
    :color="color"
    :rounded="rounded"
    v-bind="$attrs"
  >
    <!-- Header opcional -->
    <v-card-title
      v-if="title || $slots.title"
      class="biuai-card-title"
      :class="titleClass"
    >
      <slot name="title">
        <div class="d-flex align-center">
          <v-icon
            v-if="icon"
            :icon="icon"
            :color="iconColor"
            class="me-3"
            size="large"
          />
          <div>
            <h3 class="text-h6 font-weight-bold">{{ title }}</h3>
            <p v-if="subtitle" class="text-caption text-medium-emphasis mb-0">
              {{ subtitle }}
            </p>
          </div>
        </div>
      </slot>
    </v-card-title>

    <!-- Conteúdo principal -->
    <v-card-text
      v-if="$slots.default"
      :class="contentClass"
    >
      <slot />
    </v-card-text>

    <!-- Actions opcionais -->
    <v-card-actions
      v-if="$slots.actions"
      class="biuai-card-actions"
      :class="actionsClass"
    >
      <slot name="actions" />
    </v-card-actions>

    <!-- Loading overlay -->
    <v-overlay
      v-if="loading"
      :model-value="loading"
      contained
      class="align-center justify-center"
    >
      <v-progress-circular
        color="primary"
        indeterminate
        size="48"
      />
    </v-overlay>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

defineOptions({
  inheritAttrs: false
})

const props = defineProps({
  // Conteúdo
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
    default: ''
  },
  iconColor: {
    type: String,
    default: 'primary'
  },

  // Aparência
  variant: {
    type: String,
    default: 'elevated',
    validator: (value) => ['flat', 'elevated', 'tonal', 'outlined', 'text', 'plain'].includes(value)
  },
  color: {
    type: String,
    default: ''
  },
  rounded: {
    type: [String, Number, Boolean],
    default: 'lg'
  },
  elevation: {
    type: [String, Number],
    default: null
  },

  // Tipo especial
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'success', 'error', 'warning', 'info'].includes(value)
  },

  // Estados
  loading: {
    type: Boolean,
    default: false
  },
  hover: {
    type: Boolean,
    default: false
  },

  // Classes customizadas
  titleClass: {
    type: [String, Array, Object],
    default: ''
  },
  contentClass: {
    type: [String, Array, Object],
    default: ''
  },
  actionsClass: {
    type: [String, Array, Object],
    default: ''
  }
})

const cardClass = computed(() => {
  const classes = ['biuai-card']
  
  if (props.type !== 'default') {
    classes.push(`biuai-card--${props.type}`)
  }
  
  if (props.hover) {
    classes.push('biuai-card--hover')
  }
  
  return classes
})

const computedElevation = computed(() => {
  if (props.elevation !== null) {
    return props.elevation
  }
  
  switch (props.type) {
    case 'success':
    case 'error':
    case 'warning':
    case 'info':
      return 4
    default:
      return 2
  }
})
</script>

<style lang="scss" scoped>
.biuai-card {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  
  &--hover:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
  }
  
  &--success {
    border-left: 4px solid rgb(var(--v-theme-success));
  }
  
  &--error {
    border-left: 4px solid rgb(var(--v-theme-error));
  }
  
  &--warning {
    border-left: 4px solid rgb(var(--v-theme-warning));
  }
  
  &--info {
    border-left: 4px solid rgb(var(--v-theme-info));
  }
}

.biuai-card-title {
  padding: 20px 24px 12px 24px;
}

.biuai-card-actions {
  padding: 12px 24px 20px 24px;
}
</style> 