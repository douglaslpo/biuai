<template>
  <div class="biuai-input-wrapper">
    <!-- Label personalizada -->
    <label
      v-if="label && showLabel"
      :for="inputId"
      class="biuai-input-label"
      :class="labelClass"
    >
      {{ label }}
      <span v-if="required" class="text-error ml-1">*</span>
    </label>

    <!-- Campo de input -->
    <v-text-field
      :id="inputId"
      :model-value="modelValue"
      :type="computedType"
      :label="showLabel ? undefined : label"
      :placeholder="placeholder"
      :rules="computedRules"
      :error-messages="errorMessages"
      :hint="hint"
      :persistent-hint="persistentHint"
      :prepend-inner-icon="prependInnerIcon"
      :append-inner-icon="computedAppendIcon"
      :variant="variant"
      :density="density"
      :clearable="clearable"
      :disabled="disabled"
      :readonly="readonly"
      :loading="loading"
      :hide-details="hideDetails"
      :class="inputClass"
      v-bind="$attrs"
      @update:model-value="updateValue"
      @click:append-inner="handleAppendClick"
      @focus="handleFocus"
      @blur="handleBlur"
    />

    <!-- Mensagem de ajuda -->
    <div
      v-if="helpText && !hideDetails"
      class="biuai-input-help text-caption mt-1"
    >
      {{ helpText }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref, useId } from 'vue'

defineOptions({
  inheritAttrs: false
})

const props = defineProps({
  // Valor
  modelValue: {
    type: [String, Number],
    default: ''
  },

  // Configuração básica
  type: {
    type: String,
    default: 'text',
    validator: (value) => ['text', 'password', 'email', 'number', 'tel', 'url', 'search'].includes(value)
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  hint: {
    type: String,
    default: ''
  },
  helpText: {
    type: String,
    default: ''
  },

  // Validação
  rules: {
    type: Array,
    default: () => []
  },
  errorMessages: {
    type: [String, Array],
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },

  // Aparência
  variant: {
    type: String,
    default: 'outlined',
    validator: (value) => ['filled', 'outlined', 'underlined', 'plain', 'solo', 'solo-inverted', 'solo-filled'].includes(value)
  },
  density: {
    type: String,
    default: 'comfortable',
    validator: (value) => ['default', 'comfortable', 'compact'].includes(value)
  },
  showLabel: {
    type: Boolean,
    default: false
  },

  // Ícones
  prependInnerIcon: {
    type: String,
    default: ''
  },
  appendInnerIcon: {
    type: String,
    default: ''
  },

  // Estados
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  clearable: {
    type: Boolean,
    default: false
  },

  // Controle de exibição
  hideDetails: {
    type: [Boolean, String],
    default: false
  },
  persistentHint: {
    type: Boolean,
    default: false
  },

  // Classes customizadas
  labelClass: {
    type: [String, Array, Object],
    default: ''
  },
  inputClass: {
    type: [String, Array, Object],
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'focus', 'blur', 'append-click'])

// ID único para acessibilidade
const inputId = useId()

// Estado da senha
const showPassword = ref(false)

const computedType = computed(() => {
  if (props.type === 'password') {
    return showPassword.value ? 'text' : 'password'
  }
  return props.type
})

const computedAppendIcon = computed(() => {
  if (props.type === 'password') {
    return showPassword.value ? 'mdi-eye-off' : 'mdi-eye'
  }
  return props.appendInnerIcon
})

const computedRules = computed(() => {
  const rules = [...props.rules]
  
  if (props.required) {
    rules.unshift((value) => {
      if (!value || (typeof value === 'string' && value.trim() === '')) {
        return 'Este campo é obrigatório'
      }
      return true
    })
  }
  
  // Regras específicas por tipo
  if (props.type === 'email') {
    rules.push((value) => {
      if (!value) return true
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailPattern.test(value) || 'Email inválido'
    })
  }
  
  return rules
})

const updateValue = (value) => {
  emit('update:modelValue', value)
}

const handleAppendClick = () => {
  if (props.type === 'password') {
    showPassword.value = !showPassword.value
  } else {
    emit('append-click')
  }
}

const handleFocus = (event) => {
  emit('focus', event)
}

const handleBlur = (event) => {
  emit('blur', event)
}
</script>

<style lang="scss" scoped>
.biuai-input-wrapper {
  width: 100%;
}

.biuai-input-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgb(var(--v-theme-on-surface));
  margin-bottom: 8px;
  line-height: 1.4;
}

.biuai-input-help {
  color: rgba(var(--v-theme-on-surface), 0.6);
  line-height: 1.4;
}

// Customizações do Vuetify
:deep(.v-field) {
  border-radius: 8px !important;
  
  &:hover .v-field__outline {
    --v-field-border-opacity: 0.24;
  }
  
  &.v-field--focused .v-field__outline {
    --v-field-border-width: 2px;
  }
}

:deep(.v-field__input) {
  font-size: 1rem;
  line-height: 1.5;
  padding: 12px 16px;
}

:deep(.v-field-label) {
  font-size: 1rem;
  font-weight: 400;
}

:deep(.v-input__prepend-inner),
:deep(.v-input__append-inner) {
  padding-top: 12px;
}

// Estados especiais
.biuai-input-wrapper:has(.v-input--error) {
  .biuai-input-label {
    color: rgb(var(--v-theme-error));
  }
}

.biuai-input-wrapper:has(.v-input--disabled) {
  .biuai-input-label {
    color: rgba(var(--v-theme-on-surface), 0.38);
  }
}
</style> 