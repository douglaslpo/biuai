<template>
  <div class="metas-page">
    <!-- Page Header -->
    <PageHeader
      title="Metas Financeiras"
      subtitle="Defina e acompanhe seus objetivos financeiros com inteligência"
      icon="mdi-target"
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
          Nova Meta
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
              label="Total de Metas"
              :value="metrics.totalMetas"
              icon="mdi-target"
              color="primary"
            />
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Metas Ativas"
              :value="metrics.metasAtivas"
              icon="mdi-clock-outline"
              color="info"
            />
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Metas Concluídas"
              :value="metrics.metasConcluidas"
              icon="mdi-check-circle"
              color="success"
            />
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Taxa de Sucesso"
              :value="metrics.taxaSucesso"
              format="percentage"
              icon="mdi-chart-line"
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
            v-model="filters.status"
            :items="statusOptions"
            label="Status"
            density="comfortable"
            variant="outlined"
            clearable
          />
        </v-col>
        
        <v-col cols="12" md="3">
          <v-select
            v-model="filters.categoria"
            :items="categoriasOptions"
            label="Categoria"
            density="comfortable"
            variant="outlined"
            clearable
          />
        </v-col>
        
        <v-col cols="12" md="4">
          <v-text-field
            v-model="searchQuery"
            label="Pesquisar metas..."
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
            Limpar
          </v-btn>
        </v-col>
      </v-row>
    </BaseCard>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <v-progress-circular size="64" color="primary" indeterminate />
      <p class="mt-4 text-h6">Carregando metas...</p>
    </div>

    <!-- Empty State -->
    <BaseCard v-else-if="isEmpty" class="text-center py-12">
      <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-target-off</v-icon>
      <h3 class="text-h5 mb-2">Nenhuma meta encontrada</h3>
      <p class="text-body-1 mb-4">Comece definindo suas primeiras metas financeiras</p>
      <v-btn
        color="primary"
        variant="elevated"
        prepend-icon="mdi-plus"
        @click="showCreateDialog = true"
      >
        Criar Primeira Meta
      </v-btn>
    </BaseCard>

    <!-- Metas Grid -->
    <v-row v-else>
      <v-col
        v-for="meta in paginatedData"
        :key="meta.id"
        cols="12"
        md="6"
        lg="4"
      >
        <MetaCard
          :meta="meta"
          @edit="editMeta"
          @delete="confirmDelete"
          @view="viewMeta"
        />
      </v-col>
    </v-row>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="d-flex justify-center mt-6">
      <v-pagination
        v-model="currentPage"
        :length="totalPages"
        :total-visible="7"
        @update:model-value="goToPage"
      />
    </div>

    <!-- Create/Edit Dialog -->
    <MetaDialog
      v-model="showCreateDialog"
      :meta="editingMeta"
      :loading="dialogLoading"
      @save="handleSave"
      @cancel="handleCancel"
    />

    <!-- Delete Confirmation -->
    <ConfirmDialog
      v-model="showDeleteDialog"
      title="Confirmar Exclusão"
      :message="`Tem certeza que deseja excluir a meta '${deletingMeta?.descricao}'?`"
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
import { useNotifications } from '@/composables/useNotifications'
import { metasService } from '@/services/metas'

// Components
import PageHeader from '@/components/base/PageHeader.vue'
import MetricCard from '@/components/base/MetricCard.vue'
import BaseCard from '@/components/base/BaseCard.vue'
import MetaCard from '@/components/forms/MetaCard.vue'
import MetaDialog from '@/components/modals/MetaDialog.vue'
import ConfirmDialog from '@/components/modals/ConfirmDialog.vue'

// Composables
const {
  data: metas,
  paginatedData,
  loading,
  isEmpty,
  searchQuery,
  filters,
  currentPage,
  totalPages,
  setSearch,
  clearFilters,
  refresh,
  goToPage,
  addItem,
  updateItem,
  removeItem
} = usePageData({
  fetchFn: metasService.list,
  autoFetch: true,
  pageSize: 12
})

const { showActionSuccess, showActionError } = useNotifications()

// Local state
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const editingMeta = ref(null)
const deletingMeta = ref(null)
const dialogLoading = ref(false)

// Options
const statusOptions = [
  { title: 'Ativa', value: 'ativa' },
  { title: 'Concluída', value: 'concluida' },
  { title: 'Pausada', value: 'pausada' },
  { title: 'Vencida', value: 'vencida' }
]

const categoriasOptions = [
  { title: 'Economia', value: 'economia' },
  { title: 'Investimento', value: 'investimento' },
  { title: 'Compra', value: 'compra' },
  { title: 'Viagem', value: 'viagem' },
  { title: 'Emergência', value: 'emergencia' }
]

// Computed
const metrics = computed(() => {
  const total = metas.value.length
  const ativas = metas.value.filter(m => m.status === 'ativa').length
  const concluidas = metas.value.filter(m => m.status === 'concluida').length
  const taxaSucesso = total > 0 ? (concluidas / total) * 100 : 0

  return {
    totalMetas: total,
    metasAtivas: ativas,
    metasConcluidas: concluidas,
    taxaSucesso: Math.round(taxaSucesso)
  }
})

// Methods
const editMeta = (meta) => {
  editingMeta.value = { ...meta }
  showCreateDialog.value = true
}

const confirmDelete = (meta) => {
  deletingMeta.value = meta
  showDeleteDialog.value = true
}

const viewMeta = (meta) => {
  console.log('View meta:', meta)
}

const handleSave = async (metaData) => {
  try {
    dialogLoading.value = true
    
    if (editingMeta.value?.id) {
      const updated = await metasService.update(editingMeta.value.id, metaData)
      updateItem(editingMeta.value.id, updated)
      showActionSuccess('update', 'Meta')
    } else {
      const created = await metasService.create(metaData)
      addItem(created)
      showActionSuccess('create', 'Meta')
    }
    
    handleCancel()
    
  } catch (error) {
    showActionError(editingMeta.value?.id ? 'update' : 'create', 'meta', error.message)
  } finally {
    dialogLoading.value = false
  }
}

const handleCancel = () => {
  showCreateDialog.value = false
  editingMeta.value = null
  dialogLoading.value = false
}

const handleDelete = async () => {
  try {
    await metasService.delete(deletingMeta.value.id)
    removeItem(deletingMeta.value.id)
    showActionSuccess('delete', 'Meta')
    
  } catch (error) {
    showActionError('delete', 'meta', error.message)
  } finally {
    showDeleteDialog.value = false
    deletingMeta.value = null
  }
}

// Lifecycle
onMounted(() => {
  // Additional setup if needed
})
</script>

<style scoped>
.metas-page {
  padding: 0;
}

/* Responsividade */
@media (max-width: 768px) {
  .metas-page :deep(.header-actions) {
    flex-direction: column;
    gap: 8px;
  }
  
  .metas-page :deep(.header-actions .v-btn) {
    width: 100%;
  }
}
</style> 