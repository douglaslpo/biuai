<template>
  <div class="biuai-lancamentos">
    <!-- Header da página -->
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="biuai-text-h3 text-primary mb-2">
          📋 Lançamentos Financeiros
        </h1>
        <p class="text-body-1 text-medium-emphasis">
          Gerencie suas receitas e despesas de forma eficiente
        </p>
      </div>
      <div class="d-flex ga-3">
        <BaseButton
          type="primary"
          prepend-icon="mdi-plus"
          @click="showNewLancamento = true"
          size="default"
        >
          Novo Lançamento
        </BaseButton>
        <BaseButton
          variant="outlined"
          icon="mdi-refresh"
          :loading="loading"
          @click="refreshData"
          size="default"
        />
        <BaseButton
          type="secondary"
          prepend-icon="mdi-download"
          @click="exportData"
          size="default"
        >
          Exportar
        </BaseButton>
      </div>
    </div>

    <!-- Filtros e busca -->
    <BaseCard
      title="🔍 Filtros e Busca"
      subtitle="Encontre rapidamente os lançamentos desejados"
      icon="mdi-filter"
      class="mb-6"
    >
      <v-row>
        <!-- Busca por texto -->
        <v-col cols="12" md="4">
          <v-text-field
            v-model="search"
            label="Buscar lançamentos"
            placeholder="Descrição, categoria, órgão..."
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            density="comfortable"
            clearable
            @keyup.enter="searchLancamentos"
          />
        </v-col>

        <!-- Filtro por tipo -->
        <v-col cols="12" md="2">
          <v-select
            v-model="filters.tipo"
            :items="tipoOptions"
            label="Tipo"
            prepend-inner-icon="mdi-format-list-bulleted-type"
            variant="outlined"
            density="comfortable"
            clearable
          />
        </v-col>

        <!-- Filtro por categoria -->
        <v-col cols="12" md="2">
          <v-autocomplete
            v-model="filters.categoria"
            :items="categorias"
            label="Categoria"
            prepend-inner-icon="mdi-tag"
            variant="outlined"
            density="comfortable"
            clearable
          />
        </v-col>

        <!-- Data inicial -->
        <v-col cols="12" md="2">
          <v-text-field
            v-model="filters.data_inicial"
            label="Data inicial"
            prepend-inner-icon="mdi-calendar-start"
            variant="outlined"
            density="comfortable"
            type="date"
            clearable
          />
        </v-col>

        <!-- Data final -->
        <v-col cols="12" md="2">
          <v-text-field
            v-model="filters.data_final"
            label="Data final"
            prepend-inner-icon="mdi-calendar-end"
            variant="outlined"
            density="comfortable"
            type="date"
            clearable
          />
        </v-col>
      </v-row>

      <template #actions>
        <BaseButton
          variant="text"
          prepend-icon="mdi-filter-remove"
          @click="clearFilters"
          size="small"
        >
          Limpar Filtros
        </BaseButton>
        <BaseButton
          type="primary"
          prepend-icon="mdi-magnify"
          @click="searchLancamentos"
          size="small"
        >
          Buscar
        </BaseButton>
      </template>
    </BaseCard>

    <!-- Resumo dos filtros aplicados -->
    <div v-if="hasActiveFilters" class="mb-4">
      <div class="d-flex flex-wrap ga-2 align-center">
        <span class="text-body-2 text-medium-emphasis">Filtros ativos:</span>
        <v-chip
          v-if="filters.tipo"
          :color="filters.tipo === 'RECEITA' ? 'success' : 'error'"
          size="small"
          closable
          @click:close="filters.tipo = null"
        >
          {{ filters.tipo }}
        </v-chip>
        <v-chip
          v-if="filters.categoria"
          color="primary"
          size="small"
          closable
          @click:close="filters.categoria = null"
        >
          {{ filters.categoria }}
        </v-chip>
        <v-chip
          v-if="filters.data_inicial"
          color="info"
          size="small"
          closable
          @click:close="filters.data_inicial = null"
        >
          A partir de {{ formatDate(filters.data_inicial) }}
        </v-chip>
        <v-chip
          v-if="filters.data_final"
          color="info"
          size="small"
          closable
          @click:close="filters.data_final = null"
        >
          Até {{ formatDate(filters.data_final) }}
        </v-chip>
      </div>
    </div>

    <!-- Lista de lançamentos -->
    <BaseCard
      :title="`💰 Lançamentos (${totalItems})`"
      :subtitle="getSubtitleText()"
      icon="mdi-format-list-bulleted"
      hover
    >
      <template #actions>
        <v-btn-toggle
          v-model="viewMode"
          color="primary"
          variant="outlined"
          divided
          density="compact"
        >
          <v-btn value="list" icon="mdi-format-list-bulleted" />
          <v-btn value="cards" icon="mdi-view-grid" />
          <v-btn value="table" icon="mdi-table" />
        </v-btn-toggle>
      </template>

      <!-- Loading state -->
      <div v-if="loading" class="text-center py-8">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        />
        <p class="text-body-1 mt-4">Carregando lançamentos...</p>
      </div>

      <!-- Empty state -->
      <div v-else-if="!lancamentos.length" class="text-center py-12">
        <v-icon
          icon="mdi-receipt-text-outline"
          size="96"
          color="grey-lighten-1"
          class="mb-4"
        />
        <h3 class="text-h5 mb-2">Nenhum lançamento encontrado</h3>
        <p class="text-body-1 text-medium-emphasis mb-6">
          {{ hasActiveFilters 
            ? 'Tente ajustar os filtros de busca' 
            : 'Comece criando seu primeiro lançamento financeiro' 
          }}
        </p>
        <BaseButton
          v-if="!hasActiveFilters"
          type="primary"
          prepend-icon="mdi-plus"
          @click="showNewLancamento = true"
          size="large"
        >
          Criar Primeiro Lançamento
        </BaseButton>
        <BaseButton
          v-else
          variant="outlined"
          prepend-icon="mdi-filter-remove"
          @click="clearFilters"
          size="large"
        >
          Limpar Filtros
        </BaseButton>
      </div>

      <!-- List view -->
      <v-list
        v-else-if="viewMode === 'list'"
        class="pa-0"
      >
        <v-list-item
          v-for="(lancamento, index) in lancamentos"
          :key="lancamento.id"
          @click="editLancamento(lancamento)"
          class="rounded-lg mb-2 biuai-lancamento-item"
          color="primary"
        >
          <template #prepend>
            <v-avatar
              :color="lancamento.tipo === 'RECEITA' ? 'success' : 'error'"
              size="48"
              class="me-4"
            >
              <v-icon
                :icon="lancamento.tipo === 'RECEITA' ? 'mdi-plus' : 'mdi-minus'"
                color="white"
                size="24"
              />
            </v-avatar>
          </template>

          <v-list-item-title class="font-weight-medium text-h6 mb-1">
            {{ lancamento.descricao }}
          </v-list-item-title>
          <v-list-item-subtitle class="d-flex flex-wrap ga-2 align-center">
            <v-chip
              :color="lancamento.tipo === 'RECEITA' ? 'success' : 'error'"
              size="x-small"
              variant="flat"
            >
              {{ lancamento.tipo }}
            </v-chip>
            <span>{{ formatDate(lancamento.data_lancamento) }}</span>
            <v-chip
              v-if="lancamento.categoria"
              color="primary"
              size="x-small"
              variant="outlined"
            >
              {{ lancamento.categoria }}
            </v-chip>
            <span v-if="lancamento.orgao_nome" class="text-caption">
              • {{ lancamento.orgao_nome }}
            </span>
          </v-list-item-subtitle>

          <template #append>
            <div class="text-end">
              <div
                class="text-h6 font-weight-bold mb-1"
                :class="lancamento.tipo === 'RECEITA' ? 'text-success' : 'text-error'"
              >
                {{ formatCurrency(lancamento.valor) }}
              </div>
              <div class="d-flex ga-1">
                <BaseButton
                  variant="text"
                  icon="mdi-pencil"
                  size="small"
                  @click.stop="editLancamento(lancamento)"
                />
                <BaseButton
                  variant="text"
                  icon="mdi-delete"
                  color="error"
                  size="small"
                  @click.stop="confirmDelete(lancamento)"
                />
              </div>
            </div>
          </template>
        </v-list-item>
      </v-list>

      <!-- Cards view -->
      <v-row v-else-if="viewMode === 'cards'">
        <v-col
          v-for="lancamento in lancamentos"
          :key="lancamento.id"
          cols="12"
          md="6"
          lg="4"
        >
          <v-card
            :color="lancamento.tipo === 'RECEITA' ? 'success' : 'error'"
            variant="tonal"
            class="biuai-lancamento-card"
            @click="editLancamento(lancamento)"
          >
            <v-card-text>
              <div class="d-flex align-center mb-3">
                <v-avatar
                  :color="lancamento.tipo === 'RECEITA' ? 'success' : 'error'"
                  size="40"
                  class="me-3"
                >
                  <v-icon
                    :icon="lancamento.tipo === 'RECEITA' ? 'mdi-plus' : 'mdi-minus'"
                    color="white"
                  />
                </v-avatar>
                <div class="flex-1-1">
                  <div class="font-weight-bold text-h6">
                    {{ lancamento.descricao }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ formatDate(lancamento.data_lancamento) }}
                  </div>
                </div>
              </div>

              <div
                class="text-h5 font-weight-bold mb-2"
                :class="lancamento.tipo === 'RECEITA' ? 'text-success-darken-2' : 'text-error-darken-2'"
              >
                {{ formatCurrency(lancamento.valor) }}
              </div>

              <div class="d-flex flex-wrap ga-1 mb-3">
                <v-chip
                  v-if="lancamento.categoria"
                  size="small"
                  variant="outlined"
                >
                  {{ lancamento.categoria }}
                </v-chip>
                <v-chip
                  v-if="lancamento.orgao_nome"
                  size="small"
                  variant="flat"
                >
                  {{ lancamento.orgao_nome }}
                </v-chip>
              </div>

              <div class="d-flex justify-end ga-2">
                <BaseButton
                  variant="text"
                  icon="mdi-pencil"
                  size="small"
                  @click.stop="editLancamento(lancamento)"
                />
                <BaseButton
                  variant="text"
                  icon="mdi-delete"
                  color="error"
                  size="small"
                  @click.stop="confirmDelete(lancamento)"
                />
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Table view -->
      <v-data-table
        v-else-if="viewMode === 'table'"
        :headers="tableHeaders"
        :items="lancamentos"
        :loading="loading"
        item-value="id"
        class="biuai-data-table"
        density="comfortable"
        hover
      >
        <template #item.tipo="{ item }">
          <v-chip
            :color="item.tipo === 'RECEITA' ? 'success' : 'error'"
            size="small"
            variant="flat"
          >
            <v-icon
              :icon="item.tipo === 'RECEITA' ? 'mdi-plus' : 'mdi-minus'"
              start
              size="small"
            />
            {{ item.tipo }}
          </v-chip>
        </template>

        <template #item.valor="{ item }">
          <span
            class="font-weight-bold"
            :class="item.tipo === 'RECEITA' ? 'text-success' : 'text-error'"
          >
            {{ formatCurrency(item.valor) }}
          </span>
        </template>

        <template #item.data_lancamento="{ item }">
          {{ formatDate(item.data_lancamento) }}
        </template>

        <template #item.categoria="{ item }">
          <v-chip
            v-if="item.categoria"
            size="small"
            variant="outlined"
          >
            {{ item.categoria }}
          </v-chip>
          <span v-else class="text-medium-emphasis">—</span>
        </template>

        <template #item.actions="{ item }">
          <div class="d-flex ga-1">
            <BaseButton
              variant="text"
              icon="mdi-pencil"
              size="small"
              @click="editLancamento(item)"
            />
            <BaseButton
              variant="text"
              icon="mdi-delete"
              color="error"
              size="small"
              @click="confirmDelete(item)"
            />
          </div>
        </template>
      </v-data-table>

      <!-- Paginação -->
      <div v-if="totalPages > 1" class="d-flex justify-center mt-6">
        <v-pagination
          v-model="currentPage"
          :length="totalPages"
          :total-visible="7"
          @update:model-value="loadLancamentos"
        />
      </div>
    </BaseCard>

    <!-- Estatísticas rápidas -->
    <v-row class="mt-6">
      <v-col cols="12" md="3">
        <BaseCard
          title="💰 Total Receitas"
          type="success"
          class="text-center"
        >
          <div class="text-h4 font-weight-bold text-success">
            {{ formatCurrency(stats.total_receitas) }}
          </div>
          <div class="text-caption text-medium-emphasis">
            {{ stats.count_receitas }} lançamentos
          </div>
        </BaseCard>
      </v-col>

      <v-col cols="12" md="3">
        <BaseCard
          title="💸 Total Despesas"
          type="error"
          class="text-center"
        >
          <div class="text-h4 font-weight-bold text-error">
            {{ formatCurrency(stats.total_despesas) }}
          </div>
          <div class="text-caption text-medium-emphasis">
            {{ stats.count_despesas }} lançamentos
          </div>
        </BaseCard>
      </v-col>

      <v-col cols="12" md="3">
        <BaseCard
          title="⚖️ Saldo Atual"
          :type="stats.saldo >= 0 ? 'success' : 'warning'"
          class="text-center"
        >
          <div 
            class="text-h4 font-weight-bold"
            :class="stats.saldo >= 0 ? 'text-success' : 'text-warning'"
          >
            {{ formatCurrency(stats.saldo) }}
          </div>
          <div class="text-caption text-medium-emphasis">
            {{ stats.saldo >= 0 ? 'Positivo' : 'Atenção' }}
          </div>
        </BaseCard>
      </v-col>

      <v-col cols="12" md="3">
        <BaseCard
          title="📊 Ticket Médio"
          type="info"
          class="text-center"
        >
          <div class="text-h4 font-weight-bold text-info">
            {{ formatCurrency(stats.ticket_medio) }}
          </div>
          <div class="text-caption text-medium-emphasis">
            Por lançamento
          </div>
        </BaseCard>
      </v-col>
    </v-row>

    <!-- Dialogs -->
    <LancamentoForm
      v-model="showNewLancamento"
      :lancamento="selectedLancamento"
      @saved="handleLancamentoSaved"
    />

    <v-dialog v-model="showDeleteDialog" max-width="400">
      <BaseCard
        title="🗑️ Confirmar Exclusão"
        subtitle="Esta ação não pode ser desfeita"
        icon="mdi-delete-alert"
        type="error"
      >
        <p class="text-body-1">
          Tem certeza que deseja excluir o lançamento
          <strong>"{{ selectedLancamento?.descricao }}"</strong>?
        </p>

        <template #actions>
          <v-spacer />
          <BaseButton
            variant="text"
            @click="showDeleteDialog = false"
          >
            Cancelar
          </BaseButton>
          <BaseButton
            type="error"
            :loading="deleting"
            @click="deleteLancamento"
          >
            Excluir
          </BaseButton>
        </template>
      </BaseCard>
    </v-dialog>

    <!-- Floating Action Button -->
    <v-fab
      icon="mdi-plus"
      location="bottom end"
      size="large"
      color="primary"
      @click="showNewLancamento = true"
      class="biuai-fab"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useLancamentosStore } from '@/stores/lancamentos'
import BaseCard from '@/components/base/BaseCard.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import LancamentoForm from '@/components/LancamentoForm.vue'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

const lancamentosStore = useLancamentosStore()

// Estados reativos
const loading = ref(false)
const deleting = ref(false)
const showNewLancamento = ref(false)
const showDeleteDialog = ref(false)
const selectedLancamento = ref(null)
const viewMode = ref('list')

// Dados
const lancamentos = ref([])
const categorias = ref([])
const totalItems = ref(0)
const currentPage = ref(1)
const itemsPerPage = ref(20)

// Busca e filtros
const search = ref('')
const filters = ref({
  tipo: null,
  categoria: null,
  data_inicial: null,
  data_final: null
})

// Opções
const tipoOptions = [
  { title: 'Receita', value: 'RECEITA' },
  { title: 'Despesa', value: 'DESPESA' }
]

const tableHeaders = [
  { title: 'Tipo', key: 'tipo', sortable: false, width: '100px' },
  { title: 'Descrição', key: 'descricao', sortable: true },
  { title: 'Valor', key: 'valor', sortable: true, width: '150px' },
  { title: 'Data', key: 'data_lancamento', sortable: true, width: '120px' },
  { title: 'Categoria', key: 'categoria', sortable: false, width: '130px' },
  { title: 'Órgão', key: 'orgao_nome', sortable: false },
  { title: 'Ações', key: 'actions', sortable: false, width: '100px' }
]

// Computed
const totalPages = computed(() => {
  return Math.ceil(totalItems.value / itemsPerPage.value)
})

const hasActiveFilters = computed(() => {
  return !!(search.value || filters.value.tipo || filters.value.categoria || 
           filters.value.data_inicial || filters.value.data_final)
})

const stats = computed(() => {
  const receitas = lancamentos.value.filter(l => l.tipo === 'RECEITA')
  const despesas = lancamentos.value.filter(l => l.tipo === 'DESPESA')
  
  const total_receitas = receitas.reduce((sum, l) => sum + parseFloat(l.valor || 0), 0)
  const total_despesas = despesas.reduce((sum, l) => sum + parseFloat(l.valor || 0), 0)
  const saldo = total_receitas - total_despesas
  
  const total_valores = lancamentos.value.reduce((sum, l) => sum + parseFloat(l.valor || 0), 0)
  const ticket_medio = lancamentos.value.length > 0 ? total_valores / lancamentos.value.length : 0

  return {
    total_receitas,
    total_despesas,
    saldo,
    ticket_medio,
    count_receitas: receitas.length,
    count_despesas: despesas.length
  }
})

// Métodos de formatação
const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value || 0)
}

const formatDate = (date) => {
  if (!date) return ''
  try {
    return format(new Date(date), 'dd/MM/yyyy', { locale: ptBR })
  } catch (error) {
    return date
  }
}

const getSubtitleText = () => {
  if (hasActiveFilters.value) {
    return 'Resultados filtrados'
  }
  return 'Todas as movimentações financeiras'
}

// Métodos de ação
const loadLancamentos = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      limit: itemsPerPage.value,
      search: search.value,
      ...filters.value
    }

    const response = await lancamentosStore.getLancamentos(params)
    lancamentos.value = response.items || []
    totalItems.value = response.total || 0
    
    // Carregar categorias se ainda não foram carregadas
    if (!categorias.value.length) {
      categorias.value = await lancamentosStore.getCategorias()
    }
  } catch (error) {
    console.error('Erro ao carregar lançamentos:', error)
  } finally {
    loading.value = false
  }
}

const searchLancamentos = () => {
  currentPage.value = 1
  loadLancamentos()
}

const clearFilters = () => {
  search.value = ''
  filters.value = {
    tipo: null,
    categoria: null,
    data_inicial: null,
    data_final: null
  }
  searchLancamentos()
}

const refreshData = () => {
  loadLancamentos()
}

const editLancamento = (lancamento) => {
  selectedLancamento.value = lancamento
  showNewLancamento.value = true
}

const confirmDelete = (lancamento) => {
  selectedLancamento.value = lancamento
  showDeleteDialog.value = true
}

const deleteLancamento = async () => {
  if (!selectedLancamento.value) return

  deleting.value = true
  try {
    await lancamentosStore.deleteLancamento(selectedLancamento.value.id)
    showDeleteDialog.value = false
    selectedLancamento.value = null
    await loadLancamentos()
  } catch (error) {
    console.error('Erro ao excluir lançamento:', error)
  } finally {
    deleting.value = false
  }
}

const handleLancamentoSaved = () => {
  showNewLancamento.value = false
  selectedLancamento.value = null
  loadLancamentos()
}

const exportData = async () => {
  try {
    const params = {
      search: search.value,
      ...filters.value,
      format: 'csv'
    }
    
    await lancamentosStore.exportLancamentos(params)
  } catch (error) {
    console.error('Erro ao exportar dados:', error)
  }
}

// Watchers
watch([() => filters.value.tipo, () => filters.value.categoria, 
       () => filters.value.data_inicial, () => filters.value.data_final], () => {
  searchLancamentos()
})

// Lifecycle
onMounted(() => {
  loadLancamentos()
})
</script>

<style lang="scss" scoped>
.biuai-lancamentos {
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
}

.biuai-lancamento-item {
  transition: all 0.3s ease;
  border: 1px solid transparent;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(var(--v-theme-primary), 0.15);
    border-color: rgba(var(--v-theme-primary), 0.3);
  }
}

.biuai-lancamento-card {
  transition: all 0.3s ease;
  cursor: pointer;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
}

.biuai-data-table {
  :deep(.v-data-table__tr:hover) {
    background-color: rgba(var(--v-theme-primary), 0.05);
  }
}

.biuai-fab {
  :deep(.v-fab) {
    box-shadow: 0 8px 24px rgba(var(--v-theme-primary), 0.3);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 32px rgba(var(--v-theme-primary), 0.4);
    }
  }
}

// Melhorar visual dos chips
.v-chip {
  font-weight: 500;
}

// Responsividade
@media (max-width: 960px) {
  .biuai-lancamentos {
    padding: 1rem;
  }
  
  .d-flex.justify-space-between {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
    
    .d-flex.ga-3 {
      width: 100%;
      flex-wrap: wrap;
    }
  }
}

@media (max-width: 600px) {
  .d-flex.ga-3 {
    flex-direction: column;
    width: 100%;
    
    .v-btn {
      width: 100%;
    }
  }
  
  .biuai-lancamento-item {
    .v-list-item-subtitle {
      flex-direction: column;
      align-items: flex-start !important;
      gap: 0.5rem;
    }
  }
}
</style> 