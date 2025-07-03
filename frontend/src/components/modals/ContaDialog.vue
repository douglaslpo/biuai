<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    persistent
    max-width="600px"
  >
    <v-card class="conta-dialog">
      <v-card-title class="px-6 py-4 bg-primary text-white">
        <div class="d-flex align-center">
          <v-icon size="24" class="mr-3">mdi-bank</v-icon>
          <span>{{ isEdit ? 'Editar Conta' : 'Nova Conta' }}</span>
        </div>
      </v-card-title>

      <v-card-text class="px-6 py-4">
        <v-form ref="formRef" v-model="formValid" @submit.prevent="handleSave">
          <v-row>
            <!-- Nome da Conta -->
            <v-col cols="12">
              <v-text-field
                v-model="form.nome"
                label="Nome da Conta"
                :rules="[rules.required]"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-account"
                placeholder="Ex: Conta Corrente Principal"
              />
            </v-col>

            <!-- Banco e Agência -->
            <v-col cols="12" md="6">
              <v-select
                v-model="form.banco"
                :items="bancoOptions"
                label="Banco"
                :rules="[rules.required]"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-bank"
              />
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.agencia"
                label="Agência"
                :rules="[rules.required]"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-office-building"
                placeholder="0000"
              />
            </v-col>

            <!-- Conta e Dígito -->
            <v-col cols="12" md="8">
              <v-text-field
                v-model="form.numero_conta"
                label="Número da Conta"
                :rules="[rules.required]"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-numeric"
                placeholder="00000-0"
              />
            </v-col>

            <v-col cols="12" md="4">
              <v-text-field
                v-model="form.digito"
                label="Dígito"
                :rules="[rules.required]"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-pound"
                placeholder="0"
                maxlength="2"
              />
            </v-col>

            <!-- Tipo e Saldo -->
            <v-col cols="12" md="6">
              <v-select
                v-model="form.tipo_conta"
                :items="tipoContaOptions"
                label="Tipo de Conta"
                :rules="[rules.required]"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-card-account-details"
              />
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.saldo_inicial"
                label="Saldo Inicial"
                :rules="[rules.requiredNumber]"
                variant="outlined"
                density="comfortable"
                type="number"
                step="0.01"
                prepend-inner-icon="mdi-currency-usd"
                placeholder="0,00"
              />
            </v-col>

            <!-- Status -->
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

            <!-- Conta Principal -->
            <v-col cols="12" md="6">
              <v-switch
                v-model="form.conta_principal"
                label="Conta Principal"
                color="primary"
                hide-details
                class="mt-2"
              />
              <p class="text-caption text-medium-emphasis mt-1">
                Defina como conta padrão para transações
              </p>
            </v-col>

            <!-- Limite -->
            <v-col v-if="form.tipo_conta === 'corrente'" cols="12" md="6">
              <v-text-field
                v-model="form.limite_credito"
                label="Limite de Crédito"
                variant="outlined"
                density="comfortable"
                type="number"
                step="0.01"
                min="0"
                prepend-inner-icon="mdi-credit-card"
                placeholder="0,00"
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
                placeholder="Informações adicionais sobre a conta..."
              />
            </v-col>
          </v-row>

          <!-- Info Cards (apenas na edição) -->
          <v-row v-if="isEdit && conta">
            <v-col cols="12">
              <v-card variant="outlined" class="info-card">
                <v-card-text>
                  <div class="d-flex justify-space-between align-center">
                    <div>
                      <p class="text-body-2 text-medium-emphasis mb-1">
                        Saldo Atual
                      </p>
                      <p class="text-h6 font-weight-bold" 
                         :class="saldoColor">
                        R$ {{ formatCurrency(conta.saldo_atual || form.saldo_inicial) }}
                      </p>
                    </div>
                    
                    <div v-if="form.tipo_conta === 'corrente' && form.limite_credito">
                      <p class="text-body-2 text-medium-emphasis mb-1">
                        Limite Disponível
                      </p>
                      <p class="text-h6">
                        R$ {{ formatCurrency(form.limite_credito) }}
                      </p>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
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
          {{ isEdit ? 'Atualizar' : 'Criar' }} Conta
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
  conta: {
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
  nome: '',
  banco: '',
  agencia: '',
  numero_conta: '',
  digito: '',
  tipo_conta: 'corrente',
  saldo_inicial: 0,
  limite_credito: 0,
  status: 'ativa',
  conta_principal: false,
  observacoes: ''
})

// Computed
const isEdit = computed(() => !!props.conta?.id)

const saldoColor = computed(() => {
  const saldo = props.conta?.saldo_atual || form.value.saldo_inicial
  return saldo >= 0 ? 'text-success' : 'text-error'
})

// Options
const bancoOptions = [
  { title: 'Banco do Brasil', value: 'banco_brasil' },
  { title: 'Bradesco', value: 'bradesco' },
  { title: 'Caixa Econômica Federal', value: 'caixa' },
  { title: 'Itaú', value: 'itau' },
  { title: 'Santander', value: 'santander' },
  { title: 'Nubank', value: 'nubank' },
  { title: 'Inter', value: 'inter' },
  { title: 'C6 Bank', value: 'c6_bank' },
  { title: 'BTG Pactual', value: 'btg_pactual' },
  { title: 'Sicoob', value: 'sicoob' },
  { title: 'Sicredi', value: 'sicredi' },
  { title: 'Outro', value: 'outro' }
]

const tipoContaOptions = [
  { title: 'Conta Corrente', value: 'corrente' },
  { title: 'Conta Poupança', value: 'poupanca' },
  { title: 'Conta Investimento', value: 'investimento' },
  { title: 'Conta Salário', value: 'salario' }
]

const statusOptions = [
  { title: 'Ativa', value: 'ativa' },
  { title: 'Inativa', value: 'inativa' },
  { title: 'Bloqueada', value: 'bloqueada' },
  { title: 'Encerrada', value: 'encerrada' }
]

// Validation rules
const rules = {
  required: value => !!value || 'Campo obrigatório',
  requiredNumber: value => {
    if (value === null || value === undefined || value === '') {
      return 'Campo obrigatório'
    }
    return true
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
    nome: '',
    banco: '',
    agencia: '',
    numero_conta: '',
    digito: '',
    tipo_conta: 'corrente',
    saldo_inicial: 0,
    limite_credito: 0,
    status: 'ativa',
    conta_principal: false,
    observacoes: ''
  }
}

const loadContaData = (conta) => {
  if (conta) {
    form.value = {
      nome: conta.nome || '',
      banco: conta.banco || '',
      agencia: conta.agencia || '',
      numero_conta: conta.numero_conta || '',
      digito: conta.digito || '',
      tipo_conta: conta.tipo_conta || 'corrente',
      saldo_inicial: conta.saldo_inicial || 0,
      limite_credito: conta.limite_credito || 0,
      status: conta.status || 'ativa',
      conta_principal: conta.conta_principal || false,
      observacoes: conta.observacoes || ''
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
    saldo_inicial: parseFloat(form.value.saldo_inicial) || 0,
    limite_credito: parseFloat(form.value.limite_credito) || 0
  }

  emit('save', formData)
}

const handleCancel = () => {
  emit('cancel')
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    loadContaData(props.conta)
  }
})

watch(() => props.conta, (newConta) => {
  if (props.modelValue) {
    loadContaData(newConta)
  }
})
</script>

<style scoped>
.conta-dialog {
  border-radius: 12px;
  overflow: hidden;
}

.info-card {
  background: rgba(var(--v-theme-surface-variant), 0.1);
  border-radius: 8px;
}

/* Form styling */
.conta-dialog :deep(.v-field__prepend-inner) {
  color: rgb(var(--v-theme-primary));
}

.conta-dialog :deep(.v-text-field input) {
  font-weight: 500;
}

/* Switch styling */
.conta-dialog :deep(.v-switch .v-selection-control__wrapper) {
  margin-top: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .conta-dialog {
    margin: 16px;
    max-width: calc(100vw - 32px);
  }
  
  .conta-dialog :deep(.v-card-title) {
    font-size: 1.1rem;
  }
}
</style> 