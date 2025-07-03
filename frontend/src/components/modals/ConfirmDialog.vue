<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="500"
    persistent
  >
    <v-card>
      <v-card-title class="text-h5 pa-6">
        <v-icon 
          :icon="icon" 
          :color="iconColor" 
          class="mr-3" 
        />
        {{ title }}
      </v-card-title>

      <v-card-text class="pa-6">
        <p class="text-body-1 mb-0">{{ message }}</p>
        
        <v-alert
          v-if="type === 'warning' || type === 'error'"
          :type="type"
          variant="tonal"
          class="mt-4"
          density="compact"
        >
          <template #text>
            {{ warningText }}
          </template>
        </v-alert>
      </v-card-text>

      <v-card-actions class="pa-6">
        <v-spacer />
        
        <v-btn
          variant="text"
          :disabled="loading"
          @click="handleCancel"
        >
          {{ cancelText }}
        </v-btn>
        
        <v-btn
          :color="confirmColor"
          variant="elevated"
          :loading="loading"
          @click="handleConfirm"
        >
          {{ confirmText }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Confirmar Ação'
  },
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'warning', // 'info', 'warning', 'error'
    validator: (value) => ['info', 'warning', 'error'].includes(value)
  },
  confirmText: {
    type: String,
    default: 'Confirmar'
  },
  cancelText: {
    type: String,
    default: 'Cancelar'
  },
  confirmColor: {
    type: String,
    default: 'warning'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

// Computed
const icon = computed(() => {
  const icons = {
    info: 'mdi-information',
    warning: 'mdi-alert',
    error: 'mdi-alert-circle'
  }
  return icons[props.type] || 'mdi-help-circle'
})

const iconColor = computed(() => {
  const colors = {
    info: 'info',
    warning: 'warning',
    error: 'error'
  }
  return colors[props.type] || 'primary'
})

const warningText = computed(() => {
  const texts = {
    warning: 'Esta ação pode ter consequências. Prossiga com cuidado.',
    error: 'Esta ação não pode ser desfeita. Certifique-se antes de continuar.'
  }
  return texts[props.type] || ''
})

// Methods
const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
  emit('update:modelValue', false)
}
</script>

<style scoped>
.v-card {
  border-radius: 16px;
}

.v-card-title {
  border-bottom: 1px solid rgba(var(--v-theme-surface), 0.12);
}
</style> 