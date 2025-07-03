<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    persistent
    max-width="600px"
  >
    <v-card class="meta-dialog">
      <v-card-title class="px-6 py-4 bg-primary text-white">
        <div class="d-flex align-center">
          <v-icon size="24" class="mr-3">mdi-target</v-icon>
          <span>{{ isEdit ? 'Editar Meta' : 'Nova Meta' }}</span>
        </div>
      </v-card-title>

      <v-card-text class="px-6 py-4">
        <v-form ref="formRef" v-model="formValid" @submit.prevent="handleSave">
          <v-row>
            <!-- Descrição -->
            <v-col cols="12">
              <v-text-field
                v-model="form.descricao"
                label="Descrição da Meta"
                :rules="[rules.required]"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-text"
                placeholder="Ex: Viagem para Europa"
              />
            </v-col>

            <!-- Valor e Data -->
            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.valor_objetivo"
                label="Valor Objetivo"
                :rules="[rules.required, rules.minValue]"
                variant="outlined"
                density="comfortable"
                type="number"
                step="0.01"
                min="0"
                prepend-inner-icon="mdi-currency-usd"
                placeholder="0,00"
              />
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.data_limite"
                label="Data Limite"
                :rules="[rules.required, rules.futureDate]"
                variant="outlined"
                density="comfortable"
                type="date"
                prepend-inner-icon="mdi-calendar"
              />
            </v-col>

            <!-- Categoria e Status -->
            <v-col cols="12" md="6">
              <v-select
                v-model="form.categoria"
                :items="categoriaOptions"
                label="Categoria"
                :rules="[rules.required]"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-tag"
              />
            </v-col>

            <v-col cols="12" md="6">
              <v-select
                v-model="form.status"
                :items="statusOptions"
                label="Status"
                :rules="[rules.required]"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-information"
              />
            </v-col>

            <!-- Valor Atual (apenas na edição) -->
            <v-col v-if="isEdit" cols="12" md="6">
              <v-text-field
                v-model="form.valor_atual"
                label="Valor Atual"
                :rules="[rules.minValue]"
                variant="outlined"
                density="comfortable"
                type="number"
                step="0.01"
                min="0"
                prepend-inner-icon="mdi-wallet"
                placeholder="0,00"
              />
            </v-col>

            <!-- Prioridade -->
            <v-col cols="12" :md="isEdit ? 6 : 12">
              <v-select
                v-model="form.prioridade"
                :items="prioridadeOptions"
                label="Prioridade"
                :rules="[rules.required]"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-flag"
              />
            </v-col>

            <!-- Observações -->
            <v-col cols="12">
              <v-textarea
                v-model="form.observacoes"
                label="Observações (opcional)"
                variant="outlined"
                density="comfortable"
                rows="3"
                prepend-inner-icon="mdi-note-text"
                placeholder="Detalhes adicionais sobre a meta..."
              />
            </v-col>
          </v-row>

          <!-- Progress Info (apenas na edição) -->
          <v-row v-if="isEdit && form.valor_objetivo > 0">
            <v-col cols="12">
              <div class="progress-info">
                <div class="d-flex justify-space-between mb-2">
                  <span class="text-body-2">Progresso da Meta</span>
                  <span class="text-body-2 font-weight-bold">
                    {{ progressPercentage }}%
                  </span>
                </div>
                <v-progress-linear
                  :model-value="progressPercentage"
                  :color="progressColor"
                  height="8"
                  rounded
                />
                <div class="d-flex justify-space-between mt-1">
                  <span class="text-caption">
                    R$ {{ formatCurrency(form.valor_atual || 0) }}
                  </span>
                  <span class="text-caption">
                    R$ {{ formatCurrency(form.valor_objetivo) }}
                  </span>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>

      <v-card-actions class="px-6 py-4">
        <v-spacer />
        <v-btn
          variant="outlined"
          @click="handleCancel"
          :disabled="loading"
        >
          Cancelar
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          :loading="loading"
          @click="handleSave"
          :disabled="!formValid"
        >
          {{ isEdit ? 'Atualizar' : 'Criar' }} Meta
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  meta: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'save', 'cancel'])

// Refs
const formRef = ref(null)
const formValid = ref(false)

// Form data
const form = ref({
  descricao: '',
  valor_objetivo: null,
  valor_atual: 0,
  data_limite: '',
  categoria: '',
  status: 'ativa',
  prioridade: 'media',
  observacoes: ''
})

// Computed
const isEdit = computed(() => !!props.meta?.id)

const progressPercentage = computed(() => {
  if (!form.value.valor_objetivo || !form.value.valor_atual) return 0
  const percentage = (form.value.valor_atual / form.value.valor_objetivo) * 100
  return Math.min(Math.round(percentage), 100)
})

const progressColor = computed(() => {
  const percentage = progressPercentage.value
  if (percentage >= 100) return 'success'
  if (percentage >= 75) return 'info'
  if (percentage >= 50) return 'warning'
  return 'primary'
})

// Options
const categoriaOptions = [
  { title: 'Economia', value: 'economia' },
  { title: 'Investimento', value: 'investimento' },
  { title: 'Compra', value: 'compra' },
  { title: 'Viagem', value: 'viagem' },
  { title: 'Emergência', value: 'emergencia' },
  { title: 'Educação', value: 'educacao' },
  { title: 'Casa', value: 'casa' },
  { title: 'Aposentadoria', value: 'aposentadoria' }
]

const statusOptions = [
  { title: 'Ativa', value: 'ativa' },
  { title: 'Concluída', value: 'concluida' },
  { title: 'Pausada', value: 'pausada' },
  { title: 'Vencida', value: 'vencida' }
]

const prioridadeOptions = [
  { title: 'Baixa', value: 'baixa' },
  { title: 'Média', value: 'media' },
  { title: 'Alta', value: 'alta' },
  { title: 'Urgente', value: 'urgente' }
]

// Validation rules
const rules = {
  required: value => !!value || 'Campo obrigatório',
  minValue: value => {
    if (value === null || value === undefined || value === '') return true
    return parseFloat(value) >= 0 || 'Valor deve ser maior ou igual a zero'
  },
  futureDate: value => {
    if (!value) return true
    const today = new Date()
    const selectedDate = new Date(value)
    return selectedDate >= today || 'Data deve ser futura'
  }
}

// Methods
const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value || 0)
}

const resetForm = () => {
  form.value = {
    descricao: '',
    valor_objetivo: null,
    valor_atual: 0,
    data_limite: '',
    categoria: '',
    status: 'ativa',
    prioridade: 'media',
    observacoes: ''
  }
}

const loadMetaData = (meta) => {
  if (meta) {
    form.value = {
      descricao: meta.descricao || '',
      valor_objetivo: meta.valor_objetivo || null,
      valor_atual: meta.valor_atual || 0,
      data_limite: meta.data_limite || '',
      categoria: meta.categoria || '',
      status: meta.status || 'ativa',
      prioridade: meta.prioridade || 'media',
      observacoes: meta.observacoes || ''
    }
  } else {
    resetForm()
  }
}

const handleSave = async () => {
  if (!formRef.value) return
  
  const { valid } = await formRef.value.validate()
  if (!valid) return

  // Convert string values to numbers
  const formData = {
    ...form.value,
    valor_objetivo: parseFloat(form.value.valor_objetivo) || 0,
    valor_atual: parseFloat(form.value.valor_atual) || 0
  }

  emit('save', formData)
}

const handleCancel = () => {
  emit('cancel')
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    loadMetaData(props.meta)
  }
})

watch(() => props.meta, (newMeta) => {
  if (props.modelValue) {
    loadMetaData(newMeta)
  }
})
</script>

<style scoped>
.meta-dialog {
  border-radius: 12px;
  overflow: hidden;
}

.progress-info {
  background: rgba(var(--v-theme-surface-variant), 0.1);
  border-radius: 8px;
  padding: 16px;
}

/* Form styling */
.meta-dialog :deep(.v-field__prepend-inner) {
  color: rgb(var(--v-theme-primary));
}

.meta-dialog :deep(.v-text-field input) {
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .meta-dialog {
    margin: 16px;
    max-width: calc(100vw - 32px);
  }
  
  .meta-dialog :deep(.v-card-title) {
    font-size: 1.1rem;
  }
}
</style> 