<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="600"
    persistent
  >
    <BaseCard
      :title="isEditing ? '✏️ Editar Lançamento' : '💰 Novo Lançamento'"
      :subtitle="isEditing ? 'Atualize as informações do lançamento' : 'Adicione uma nova movimentação financeira'"
      :icon="isEditing ? 'mdi-pencil' : 'mdi-plus-circle'"
      class="biuai-lancamento-form"
    >
      <v-form
        ref="formRef"
        v-model="formValid"
        @submit.prevent="handleSave"
      >
        <v-row>
          <!-- Tipo de lançamento -->
          <v-col cols="12">
            <v-card
              variant="outlined"
              class="pa-3 mb-4"
              :color="form.tipo === 'RECEITA' ? 'success' : 'error'"
            >
              <v-card-title class="text-h6 pa-0 mb-3">
                Tipo de Lançamento
              </v-card-title>
              <v-btn-toggle
                v-model="form.tipo"
                color="primary"
                variant="outlined"
                divided
                mandatory
                class="w-100"
              >
                <v-btn
                  value="RECEITA"
                  size="large"
                  class="flex-1-1"
                  :color="form.tipo === 'RECEITA' ? 'success' : 'default'"
                >
                  <v-icon start>mdi-plus-circle</v-icon>
                  Receita
                </v-btn>
                <v-btn
                  value="DESPESA"
                  size="large"
                  class="flex-1-1"
                  :color="form.tipo === 'DESPESA' ? 'error' : 'default'"
                >
                  <v-icon start>mdi-minus-circle</v-icon>
                  Despesa
                </v-btn>
              </v-btn-toggle>
            </v-card>
          </v-col>

          <!-- Descrição -->
          <v-col cols="12">
            <v-text-field
              v-model="form.descricao"
              label="Descrição"
              placeholder="Ex: Salário, Aluguel, Supermercado..."
              prepend-inner-icon="mdi-text"
              :rules="descricaoRules"
              variant="outlined"
              density="comfortable"
              required
            />
          </v-col>

          <!-- Valor e Data -->
          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.valor"
              label="Valor"
              placeholder="0,00"
              prepend-inner-icon="mdi-currency-brl"
              :rules="valorRules"
              variant="outlined"
              density="comfortable"
              type="number"
              step="0.01"
              min="0"
              required
            />
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.data_lancamento"
              label="Data do Lançamento"
              prepend-inner-icon="mdi-calendar"
              :rules="dataRules"
              variant="outlined"
              density="comfortable"
              type="date"
              required
            />
          </v-col>

          <!-- Categoria e Órgão -->
          <v-col cols="12" md="6">
            <v-autocomplete
              v-model="form.categoria"
              :items="categorias"
              label="Categoria"
              placeholder="Selecione ou digite uma categoria"
              prepend-inner-icon="mdi-tag"
              variant="outlined"
              density="comfortable"
              clearable
              chips
              closable-chips
            />
          </v-col>

          <v-col cols="12" md="6">
            <v-autocomplete
              v-model="form.orgao_nome"
              :items="orgaos"
              label="Órgão/Fonte"
              placeholder="Selecione ou digite um órgão"
              prepend-inner-icon="mdi-domain"
              variant="outlined"
              density="comfortable"
              clearable
              chips
              closable-chips
            />
          </v-col>

          <!-- Código SIOG e Observações -->
          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.codigo_siog"
              label="Código SIOG (opcional)"
              placeholder="Ex: 123456"
              prepend-inner-icon="mdi-barcode"
              variant="outlined"
              density="comfortable"
              hint="Código do Sistema Integrado de Orçamento e Gestão"
              persistent-hint
            />
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.natureza_despesa"
              label="Natureza da Despesa (opcional)"
              placeholder="Ex: 3.3.90.30"
              prepend-inner-icon="mdi-file-tree"
              variant="outlined"
              density="comfortable"
              hint="Classificação orçamentária"
              persistent-hint
            />
          </v-col>

          <!-- Observações -->
          <v-col cols="12">
            <v-textarea
              v-model="form.observacoes"
              label="Observações (opcional)"
              placeholder="Informações adicionais sobre este lançamento..."
              prepend-inner-icon="mdi-note-text"
              variant="outlined"
              density="comfortable"
              rows="3"
              auto-grow
            />
          </v-col>

          <!-- Tags personalizadas -->
          <v-col cols="12">
            <v-combobox
              v-model="form.tags"
              :items="tagsDisponiveis"
              label="Tags (opcional)"
              placeholder="Adicione tags para organizar melhor"
              prepend-inner-icon="mdi-tag-multiple"
              variant="outlined"
              density="comfortable"
              multiple
              chips
              closable-chips
              hint="Pressione Enter para adicionar uma nova tag"
              persistent-hint
            />
          </v-col>
        </v-row>
      </v-form>

      <!-- Preview do lançamento -->
      <v-card
        variant="tonal"
        :color="form.tipo === 'RECEITA' ? 'success' : 'error'"
        class="mt-4"
      >
        <v-card-text>
          <div class="d-flex align-center">
            <v-avatar
              :color="form.tipo === 'RECEITA' ? 'success' : 'error'"
              size="40"
              class="me-3"
            >
              <v-icon
                :icon="form.tipo === 'RECEITA' ? 'mdi-plus' : 'mdi-minus'"
                color="white"
              />
            </v-avatar>
            <div class="flex-1-1">
              <div class="font-weight-bold">
                {{ form.descricao || 'Descrição do lançamento' }}
              </div>
              <div class="text-caption">
                {{ formatDate(form.data_lancamento) }} • 
                {{ form.categoria || 'Sem categoria' }}
              </div>
            </div>
            <div class="text-end">
              <div 
                class="text-h6 font-weight-bold"
                :class="form.tipo === 'RECEITA' ? 'text-success' : 'text-error'"
              >
                {{ formatCurrency(form.valor) }}
              </div>
              <div class="text-caption">
                {{ form.tipo === 'RECEITA' ? 'Receita' : 'Despesa' }}
              </div>
            </div>
          </div>
        </v-card-text>
      </v-card>

      <template #actions>
        <v-spacer />
        <BaseButton
          variant="text"
          @click="handleCancel"
          :disabled="loading"
        >
          Cancelar
        </BaseButton>
        <BaseButton
          type="primary"
          :loading="loading"
          :disabled="!formValid"
          @click="handleSave"
        >
          {{ isEditing ? 'Atualizar' : 'Salvar' }}
        </BaseButton>
      </template>
    </BaseCard>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useLancamentosStore } from '@/stores/lancamentos'
import BaseCard from '@/components/base/BaseCard.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  lancamento: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'saved'])

const lancamentosStore = useLancamentosStore()

// Estados reativos
const formRef = ref(null)
const formValid = ref(false)
const loading = ref(false)

// Dados do formulário
const form = ref({
  tipo: 'DESPESA',
  descricao: '',
  valor: null,
  data_lancamento: new Date().toISOString().split('T')[0],
  categoria: '',
  orgao_nome: '',
  codigo_siog: '',
  natureza_despesa: '',
  observacoes: '',
  tags: []
})

// Dados para autocomplete
const categorias = ref([
  'Alimentação',
  'Transporte',
  'Moradia',
  'Saúde',
  'Educação',
  'Lazer',
  'Vestuário',
  'Salário',
  'Investimentos',
  'Outros'
])

const orgaos = ref([
  'Ministério da Fazenda',
  'Ministério da Educação',
  'Ministério da Saúde',
  'Prefeitura Municipal',
  'Governo do Estado',
  'Empresa Privada',
  'Freelancer',
  'Outros'
])

const tagsDisponiveis = ref([
  'mensal',
  'anual',
  'único',
  'urgente',
  'planejado',
  'imprevisto',
  'fixo',
  'variável'
])

// Computed
const isEditing = computed(() => !!props.lancamento?.id)

// Regras de validação
const descricaoRules = [
  v => !!v || 'Descrição é obrigatória',
  v => (v && v.length >= 3) || 'Descrição deve ter pelo menos 3 caracteres',
  v => (v && v.length <= 200) || 'Descrição deve ter no máximo 200 caracteres'
]

const valorRules = [
  v => !!v || 'Valor é obrigatório',
  v => (v && parseFloat(v) > 0) || 'Valor deve ser positivo',
  v => (v && parseFloat(v) <= 999999999) || 'Valor muito alto'
]

const dataRules = [
  v => !!v || 'Data é obrigatória',
  v => {
    if (!v) return true
    const date = new Date(v)
    const now = new Date()
    const maxDate = new Date()
    maxDate.setFullYear(now.getFullYear() + 1)
    return date <= maxDate || 'Data não pode ser superior a 1 ano no futuro'
  }
]

// Métodos de formatação
const formatCurrency = (value) => {
  if (!value && value !== 0) return 'R$ 0,00'
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(parseFloat(value))
}

const formatDate = (date) => {
  if (!date) return ''
  try {
    return format(new Date(date), 'dd/MM/yyyy', { locale: ptBR })
  } catch (error) {
    return date
  }
}

// Métodos de ação
const resetForm = () => {
  form.value = {
    tipo: 'DESPESA',
    descricao: '',
    valor: null,
    data_lancamento: new Date().toISOString().split('T')[0],
    categoria: '',
    orgao_nome: '',
    codigo_siog: '',
    natureza_despesa: '',
    observacoes: '',
    tags: []
  }
  
  if (formRef.value) {
    formRef.value.resetValidation()
  }
}

const loadLancamento = () => {
  if (props.lancamento && isEditing.value) {
    form.value = {
      ...props.lancamento,
      data_lancamento: props.lancamento.data_lancamento?.split('T')[0] || form.value.data_lancamento,
      tags: props.lancamento.tags || []
    }
  }
}

const handleSave = async () => {
  if (!formValid.value) {
    formRef.value?.validate()
    return
  }

  loading.value = true
  try {
    const dados = {
      ...form.value,
      valor: parseFloat(form.value.valor),
      tags: form.value.tags?.length ? form.value.tags.join(',') : ''
    }

    if (isEditing.value) {
      await lancamentosStore.updateLancamento(props.lancamento.id, dados)
    } else {
      await lancamentosStore.createLancamento(dados)
    }

    emit('saved')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar lançamento:', error)
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  emit('update:modelValue', false)
  resetForm()
}

// Watchers
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    loadLancamento()
  }
})

watch(() => props.lancamento, () => {
  if (props.modelValue) {
    loadLancamento()
  }
})

// Lifecycle
onMounted(() => {
  if (props.modelValue) {
    loadLancamento()
  }
})
</script>

<style lang="scss" scoped>
.biuai-lancamento-form {
  max-width: 100%;
  
  :deep(.v-card-text) {
    max-height: 70vh;
    overflow-y: auto;
  }
}

.flex-1-1 {
  flex: 1 1 auto;
}

// Animações para o preview
.v-card.mt-4 {
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
  }
}

// Melhorar espaçamento dos chips
:deep(.v-chip-group) {
  gap: 8px;
}

:deep(.v-field--variant-outlined) {
  .v-field__outline {
    --v-field-border-width: 1px;
  }
  
  &:hover .v-field__outline {
    --v-field-border-opacity: 0.25;
  }
  
  &.v-field--focused .v-field__outline {
    --v-field-border-width: 2px;
  }
}

// Responsividade
@media (max-width: 600px) {
  .biuai-lancamento-form {
    :deep(.v-card) {
      margin: 8px;
    }
    
    :deep(.v-card-text) {
      padding: 16px;
    }
  }
}
</style> 