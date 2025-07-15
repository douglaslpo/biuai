<template>
  <div class="contas-page">
    <!-- Page Header -->
    <PageHeader
      title="Contas Bancárias"
      subtitle="Gerencie suas contas e acompanhe saldos em tempo real"
      icon="mdi-bank"
    >
      <template #actions>
        <v-btn
          color="primary"
          size="large"
          variant="elevated"
          prepend-icon="mdi-plus"
          @click="showCreateDialog = true"
          class="mr-2"
        >
          Nova Conta
        </v-btn>
        
        <v-btn
          color="secondary"
          size="large"
          variant="outlined"
          icon="mdi-refresh"
          :loading="loading"
          @click="refresh"
        />
      </template>

      <template #metrics>
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Total de Contas"
              :value="metrics.totalContas"
              icon="mdi-bank"
              color="primary"
              :clickable="true"
              @click="setFilter('ativa', null)"
            />
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Contas Ativas"
              :value="metrics.contasAtivas"
              icon="mdi-check-circle"
              color="success"
              :clickable="true"
              @click="setFilter('ativa', true)"
            />
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Saldo Total"
              :value="metrics.saldoTotal"
              format="currency"
              icon="mdi-cash"
              color="info"
              :animated="true"
            />
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Banco Principal"
              :value="metrics.bancoPrincipal"
              icon="mdi-office-building"
              color="warning"
            />
          </v-col>
        </v-row>
      </template>
    </PageHeader>

    <!-- Filters Card -->
    <BaseCard class="mb-6" elevation="2">
      <template #title>
        <v-icon icon="mdi-filter" class="mr-2" />
        Filtros
      </template>
      
      <v-row>
        <v-col cols="12" md="3">
          <v-select
            v-model="filters.ativa"
            :items="statusOptions"
            label="Status"
            density="comfortable"
            variant="outlined"
            clearable
            @update:model-value="applyFilters"
          />
        </v-col>
        
        <v-col cols="12" md="3">
          <v-select
            v-model="filters.tipo_conta"
            :items="tiposContaOptions"
            label="Tipo de Conta"
            density="comfortable"
            variant="outlined"
            clearable
            @update:model-value="applyFilters"
          />
        </v-col>
        
        <v-col cols="12" md="4">
          <v-text-field
            v-model="searchQuery"
            label="Pesquisar contas..."
            density="comfortable"
            variant="outlined"
            prepend-inner-icon="mdi-magnify"
            clearable
            @input="setSearch"
          />
        </v-col>
        
        <v-col cols="12" md="2">
          <v-btn
            color="primary"
            variant="outlined"
            block
            @click="clearFilters"
          >
            Limpar Filtros
          </v-btn>
        </v-col>
      </v-row>
    </BaseCard>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <v-progress-circular size="64" color="primary" indeterminate />
      <p class="mt-4 text-h6">Carregando contas...</p>
    </div>

    <!-- Empty State -->
    <BaseCard v-else-if="isEmpty" class="text-center py-12">
      <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-bank-off</v-icon>
      <h3 class="text-h5 mb-2">Nenhuma conta encontrada</h3>
      <p class="text-body-1 mb-4">Comece criando sua primeira conta bancária</p>
      <v-btn
        color="primary"
        variant="elevated"
        prepend-icon="mdi-plus"
        @click="showCreateDialog = true"
      >
        Criar Primeira Conta
      </v-btn>
    </BaseCard>

    <!-- Contas List -->
    <div v-else>
      <!-- Agrupamento por Banco -->
      <div v-for="(contasBanco, banco) in contasAgrupadasPorBanco" :key="banco" class="mb-6">
        <BaseCard elevation="2">
          <template #title>
            <div class="d-flex align-center justify-space-between w-100">
              <div class="d-flex align-center">
                <v-icon icon="mdi-office-building" class="mr-3" />
                <span class="text-h6">{{ banco }}</span>
                <v-chip class="ml-3" size="small" color="primary" variant="tonal">
                  {{ contasBanco.length }} {{ contasBanco.length === 1 ? 'conta' : 'contas' }}
                </v-chip>
              </div>
              <div class="text-h6 font-weight-bold">
                {{ formatCurrency(calcularSaldoBanco(contasBanco)) }}
              </div>
            </div>
          </template>

          <v-row class="ma-0">
            <v-col
              v-for="conta in contasBanco"
              :key="conta.id"
              cols="12"
              md="6"
              lg="4"
              class="pa-2"
            >
              <ContaCard
                :conta="conta"
                @edit="editConta"
                @delete="confirmDelete"
                @view="viewConta"
              />
            </v-col>
          </v-row>
        </BaseCard>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <ContaDialog
      v-model="showCreateDialog"
      :conta="editingConta"
      :loading="dialogLoading"
      @save="handleSave"
      @cancel="handleCancel"
    />

    <!-- Delete Confirmation -->
    <ConfirmDialog
      v-model="showDeleteDialog"
      title="Confirmar Exclusão"
      :message="`Tem certeza que deseja excluir a conta '${deletingConta?.nm_conta}'?`"
      confirm-text="Excluir"
      confirm-color="error"
      @confirm="handleDelete"
      @cancel="showDeleteDialog = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePageData } from '@/composables/usePageData'
import { useMetrics } from '@/composables/useMetrics'
import { useNotifications } from '@/composables/useNotifications'
import { contasService } from '@/services/contas'

// Components
import PageHeader from '@/components/base/PageHeader.vue'
import MetricCard from '@/components/base/MetricCard.vue'
import BaseCard from '@/components/base/BaseCard.vue'
import ContaCard from '@/components/forms/ContaCard.vue'
import ContaDialog from '@/components/modals/ContaDialog.vue'
import ConfirmDialog from '@/components/modals/ConfirmDialog.vue'

// Composables
const {
  data: contas,
  filteredData,
  loading,
  isEmpty,
  searchQuery,
  filters,
  setFilter,
  setSearch,
  clearFilters,
  refresh,
  addItem,
  updateItem,
  removeItem
} = usePageData({
  fetchFn: contasService.list,
  autoFetch: true
})

const { formatCurrency } = useMetrics(contas)
const { showSuccess, showError, showActionSuccess, showActionError } = useNotifications()

// Local state
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const editingConta = ref(null)
const deletingConta = ref(null)
const dialogLoading = ref(false)

// Options
const statusOptions = [
  { title: 'Ativa', value: true },
  { title: 'Inativa', value: false }
]

const tiposContaOptions = [
  { title: 'Conta Corrente', value: 'corrente' },
  { title: 'Conta Poupança', value: 'poupanca' },
  { title: 'Conta Investimento', value: 'investimento' }
]

// Computed
const metrics = computed(() => {
  const total = contas.value.length
  const ativas = contas.value.filter(c => c.ativa).length
  const saldoTotal = contas.value.reduce((sum, c) => sum + (Number(c.saldo_atual) || 0), 0)
  
  // Banco com mais contas
  const bancoCount = {}
  contas.value.forEach(conta => {
    const banco = conta.banco?.nm_banco || 'Sem banco'
    bancoCount[banco] = (bancoCount[banco] || 0) + 1
  })
  
  const bancoPrincipal = Object.entries(bancoCount)
    .sort(([,a], [,b]) => b - a)[0]?.[0] || 'N/A'

  return {
    totalContas: total,
    contasAtivas: ativas,
    saldoTotal,
    bancoPrincipal
  }
})

const contasAgrupadasPorBanco = computed(() => {
  const grupos = {}
  
  filteredData.value.forEach(conta => {
    const banco = conta.banco?.nm_banco || 'Sem banco definido'
    if (!grupos[banco]) {
      grupos[banco] = []
    }
    grupos[banco].push(conta)
  })
  
  return grupos
})

// Methods
const calcularSaldoBanco = (contas) => {
  return contas.reduce((sum, conta) => sum + (Number(conta.saldo_atual) || 0), 0)
}

const applyFilters = () => {
  // Filters are automatically applied by the composable
}

const editConta = (conta) => {
  editingConta.value = { ...conta }
  showCreateDialog.value = true
}

const confirmDelete = (conta) => {
  deletingConta.value = conta
  showDeleteDialog.value = true
}

const viewConta = (conta) => {
  // Implementar visualização detalhada
  console.log('View conta:', conta)
}

const handleSave = async (contaData) => {
  try {
    dialogLoading.value = true
    
    if (editingConta.value?.id) {
      // Update
      const updated = await contasService.update(editingConta.value.id, contaData)
      updateItem(editingConta.value.id, updated)
      showActionSuccess('update', 'Conta')
    } else {
      // Create
      const created = await contasService.create(contaData)
      addItem(created)
      showActionSuccess('create', 'Conta')
    }
    
    handleCancel()
    
  } catch (error) {
    showActionError(editingConta.value?.id ? 'update' : 'create', 'conta', error.message)
  } finally {
    dialogLoading.value = false
  }
}

const handleCancel = () => {
  showCreateDialog.value = false
  editingConta.value = null
  dialogLoading.value = false
}

const handleDelete = async () => {
  try {
    await contasService.delete(deletingConta.value.id)
    removeItem(deletingConta.value.id)
    showActionSuccess('delete', 'Conta')
    
  } catch (error) {
    showActionError('delete', 'conta', error.message)
  } finally {
    showDeleteDialog.value = false
    deletingConta.value = null
  }
}

// Lifecycle
onMounted(() => {
  // Additional setup if needed
})
</script>

<style scoped>
.contas-page {
  padding: 0;
}

/* Responsividade aprimorada */
@media (max-width: 768px) {
  .contas-page :deep(.header-actions) {
    flex-direction: column;
    gap: 8px;
  }
  
  .contas-page :deep(.header-actions .v-btn) {
    width: 100%;
  }
}
</style> 