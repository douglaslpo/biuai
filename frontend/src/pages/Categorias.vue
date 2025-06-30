<template>
  <div class="categorias-page">
    <!-- Header da página -->
    <div class="page-header mb-6">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">
            🏷️ Gestão de Categorias
          </h1>
          <p class="page-subtitle">
            Organize suas receitas e despesas com categorias baseadas em expertise fiscal, contábil e financeira
          </p>
        </div>
        
        <div class="header-actions">
          <v-btn
            color="primary"
            size="large"
            variant="elevated"
            prepend-icon="mdi-plus"
            @click="openCreateDialog"
            class="create-btn"
          >
            <span class="font-weight-bold">Nova Categoria</span>
          </v-btn>
          
          <v-btn
            color="secondary"
            size="large"
            variant="outlined"
            prepend-icon="mdi-refresh"
            :loading="loading"
            @click="loadCategorias"
            class="refresh-btn"
          >
            Atualizar
          </v-btn>
        </div>
      </div>
    </div>

    <!-- Filtros e estatísticas -->
    <v-row class="mb-6">
      <v-col cols="12" md="8">
        <v-card elevation="4" class="filter-card">
          <v-card-title class="pa-4">
            <v-icon icon="mdi-filter" color="primary" class="mr-3" />
            <span class="text-h6 font-weight-bold">Filtros</span>
          </v-card-title>
          <v-card-text class="pa-4">
            <v-row>
              <v-col cols="12" md="4">
                <v-select
                  v-model="filtros.tipo"
                  :items="tiposOptions"
                  label="Tipo de Categoria"
                  prepend-inner-icon="mdi-tag"
                  variant="outlined"
                  clearable
                  @update:model-value="applyFilters"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="filtros.busca"
                  label="Buscar categoria"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  clearable
                  @input="applyFilters"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="filtros.expertise"
                  :items="expertiseOptions"
                  label="Área de Expertise"
                  prepend-inner-icon="mdi-account-tie"
                  variant="outlined"
                  clearable
                  @update:model-value="applyFilters"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <v-card elevation="4" class="stats-card">
          <v-card-title class="pa-4">
            <v-icon icon="mdi-chart-bar" color="primary" class="mr-3" />
            <span class="text-h6 font-weight-bold">Estatísticas</span>
          </v-card-title>
          <v-card-text class="pa-4">
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-value text-success">{{ stats.receitas }}</div>
                <div class="stat-label">Receitas</div>
              </div>
              <div class="stat-item">
                <div class="stat-value text-error">{{ stats.despesas }}</div>
                <div class="stat-label">Despesas</div>
              </div>
              <div class="stat-item">
                <div class="stat-value text-primary">{{ stats.total }}</div>
                <div class="stat-label">Total</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Lista de categorias -->
    <v-card elevation="4" class="categories-card">
      <v-card-title class="pa-6">
        <v-icon icon="mdi-view-list" color="primary" class="mr-3" />
        <span class="text-h5 font-weight-bold">Categorias</span>
        <v-spacer />
        <v-chip 
          :color="filteredCategorias.length > 0 ? 'success' : 'warning'" 
          variant="tonal"
        >
          {{ filteredCategorias.length }} categoria{{ filteredCategorias.length !== 1 ? 's' : '' }}
        </v-chip>
      </v-card-title>
      
      <v-card-text class="pa-0">
        <v-data-table
          :headers="headers"
          :items="filteredCategorias"
          :loading="loading"
          class="categories-table"
          item-key="id"
          :items-per-page="15"
          :search="filtros.busca"
        >
          <!-- Slot para tipo -->
          <template #item.tipo="{ item }">
            <v-chip
              :color="item.tipo === 'RECEITA' ? 'success' : 'error'"
              variant="elevated"
              size="small"
            >
              <v-icon 
                :icon="item.tipo === 'RECEITA' ? 'mdi-plus' : 'mdi-minus'" 
                size="small" 
                class="mr-1"
              />
              {{ item.tipo }}
            </v-chip>
          </template>

          <!-- Slot para expertise -->
          <template #item.expertise="{ item }">
            <v-chip
              :color="getExpertiseColor(item.expertise)"
              variant="tonal"
              size="small"
            >
              <v-icon 
                :icon="getExpertiseIcon(item.expertise)" 
                size="small" 
                class="mr-1"
              />
              {{ item.expertise }}
            </v-chip>
          </template>

          <!-- Slot para descrição -->
          <template #item.descricao="{ item }">
            <div class="description-cell">
              <span class="description-text">{{ item.descricao }}</span>
              <v-tooltip v-if="item.descricao && item.descricao.length > 50" activator="parent">
                {{ item.descricao }}
              </v-tooltip>
            </div>
          </template>

          <!-- Slot para ações -->
          <template #item.actions="{ item }">
            <div class="action-buttons">
              <v-btn
                icon="mdi-pencil"
                size="small"
                variant="text"
                color="primary"
                @click="editCategoria(item)"
              />
              <v-btn
                icon="mdi-delete"
                size="small"
                variant="text"
                color="error"
                @click="confirmDelete(item)"
              />
            </div>
          </template>

          <!-- Loading -->
          <template #loading>
            <v-skeleton-loader type="table-row@10" />
          </template>

          <!-- Sem dados -->
          <template #no-data>
            <div class="no-data-container">
              <v-icon icon="mdi-tag-off" size="64" color="grey" class="mb-4" />
              <p class="text-h6 text-medium-emphasis">Nenhuma categoria encontrada</p>
              <p class="text-body-2 text-medium-emphasis mb-4">
                Crie sua primeira categoria para organizar suas finanças
              </p>
              <v-btn
                color="primary"
                prepend-icon="mdi-plus"
                @click="openCreateDialog"
              >
                Criar Categoria
              </v-btn>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Dialog de criação/edição -->
    <v-dialog v-model="dialog" max-width="600px" persistent>
      <v-card class="dialog-card">
        <v-card-title class="pa-6">
          <v-icon 
            :icon="editingCategoria ? 'mdi-pencil' : 'mdi-plus'" 
            color="primary" 
            class="mr-3" 
          />
          <span class="text-h5 font-weight-bold">
            {{ editingCategoria ? 'Editar' : 'Nova' }} Categoria
          </span>
        </v-card-title>

        <v-card-text class="pa-6">
          <v-form ref="form" v-model="formValid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="categoriaForm.nome"
                  label="Nome da Categoria"
                  prepend-inner-icon="mdi-tag"
                  variant="outlined"
                  :rules="[rules.required]"
                  required
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="categoriaForm.tipo"
                  :items="tiposOptions"
                  label="Tipo"
                  prepend-inner-icon="mdi-swap-vertical"
                  variant="outlined"
                  :rules="[rules.required]"
                  required
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-select
                  v-model="categoriaForm.expertise"
                  :items="expertiseOptions"
                  label="Área de Expertise"
                  prepend-inner-icon="mdi-account-tie"
                  variant="outlined"
                  hint="Classificação baseada em conhecimento fiscal, contábil ou financeiro"
                  persistent-hint
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="categoriaForm.descricao"
                  label="Descrição"
                  prepend-inner-icon="mdi-text"
                  variant="outlined"
                  rows="3"
                  hint="Descreva o propósito e uso desta categoria"
                  persistent-hint
                />
              </v-col>
            </v-row>

            <!-- Sugestões baseadas em expertise -->
            <v-row v-if="expertiseSuggestions.length > 0">
              <v-col cols="12">
                <v-card variant="tonal" color="info" class="mt-4">
                  <v-card-title class="text-body-1 font-weight-bold">
                    <v-icon icon="mdi-lightbulb" class="mr-2" />
                    Sugestões de Especialistas
                  </v-card-title>
                  <v-card-text>
                    <div class="suggestions-grid">
                      <v-chip
                        v-for="suggestion in expertiseSuggestions"
                        :key="suggestion"
                        variant="outlined"
                        size="small"
                        clickable
                        @click="applySuggestion(suggestion)"
                        class="ma-1"
                      >
                        {{ suggestion }}
                      </v-chip>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-card-actions class="pa-6">
          <v-spacer />
          <v-btn
            variant="text"
            @click="closeDialog"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :loading="saving"
            :disabled="!formValid"
            @click="saveCategoria"
          >
            {{ editingCategoria ? 'Atualizar' : 'Criar' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog de confirmação de exclusão -->
    <v-dialog v-model="deleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h6">
          <v-icon icon="mdi-delete" color="error" class="mr-2" />
          Confirmar Exclusão
        </v-card-title>
        <v-card-text>
          Tem certeza que deseja excluir a categoria 
          <strong>{{ categoriaToDelete?.nome }}</strong>?
          <br><br>
          <v-alert
            type="warning"
            variant="tonal"
            class="mt-2"
          >
            Esta ação não pode ser desfeita. Lançamentos vinculados a esta categoria ficarão sem categoria.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="deleteDialog = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            :loading="deleting"
            @click="deleteCategoria"
          >
            Excluir
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api as axios } from '@/boot/axios'

// Estados reativos
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const dialog = ref(false)
const deleteDialog = ref(false)
const formValid = ref(false)
const form = ref(null)

// Dados
const categorias = ref([])
const editingCategoria = ref(null)
const categoriaToDelete = ref(null)

// Filtros
const filtros = ref({
  tipo: null,
  busca: '',
  expertise: null
})

// Form
const categoriaForm = ref({
  nome: '',
  tipo: '',
  descricao: '',
  expertise: ''
})

// Opções
const tiposOptions = [
  { title: 'Receita', value: 'RECEITA' },
  { title: 'Despesa', value: 'DESPESA' }
]

const expertiseOptions = [
  { title: 'Fiscal', value: 'fiscal' },
  { title: 'Contábil', value: 'contabil' },
  { title: 'Financeira', value: 'financeira' },
  { title: 'Pessoal', value: 'pessoal' },
  { title: 'Operacional', value: 'operacional' }
]

// Headers da tabela
const headers = [
  { title: 'Nome', key: 'nome', sortable: true },
  { title: 'Tipo', key: 'tipo', sortable: true },
  { title: 'Expertise', key: 'expertise', sortable: true },
  { title: 'Descrição', key: 'descricao', sortable: false },
  { title: 'Ações', key: 'actions', sortable: false, align: 'center' }
]

// Regras de validação
const rules = {
  required: value => !!value || 'Campo obrigatório'
}

// Computadas
const filteredCategorias = computed(() => {
  let filtered = [...categorias.value]

  if (filtros.value.tipo) {
    filtered = filtered.filter(cat => cat.tipo === filtros.value.tipo)
  }

  if (filtros.value.expertise) {
    filtered = filtered.filter(cat => cat.expertise === filtros.value.expertise)
  }

  if (filtros.value.busca) {
    const busca = filtros.value.busca.toLowerCase()
    filtered = filtered.filter(cat => 
      cat.nome.toLowerCase().includes(busca) ||
      cat.descricao?.toLowerCase().includes(busca)
    )
  }

  return filtered
})

const stats = computed(() => ({
  total: categorias.value.length,
  receitas: categorias.value.filter(cat => cat.tipo === 'RECEITA').length,
  despesas: categorias.value.filter(cat => cat.tipo === 'DESPESA').length
}))

const expertiseSuggestions = computed(() => {
  const suggestions = {
    fiscal: ['ICMS', 'IPI', 'PIS', 'COFINS', 'IRPJ', 'CSLL', 'ISS', 'Taxas Municipais'],
    contabil: ['CMV', 'Depreciação', 'Amortização', 'Provisões', 'Resultado Operacional'],
    financeira: ['Juros Recebidos', 'Dividendos', 'Aplicações Financeiras', 'Empréstimos'],
    pessoal: ['Alimentação', 'Transporte', 'Educação', 'Saúde', 'Moradia'],
    operacional: ['Marketing', 'Vendas', 'Administração', 'Produção', 'Logística']
  }
  
  return suggestions[categoriaForm.value.expertise] || []
})

// Métodos
const loadCategorias = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/financeiro/categorias')
    categorias.value = response.data.map(cat => ({
      ...cat,
      expertise: getExpertiseFromCategory(cat)
    }))
  } catch (error) {
    console.error('Erro ao carregar categorias:', error)
  } finally {
    loading.value = false
  }
}

const getExpertiseFromCategory = (categoria) => {
  const nome = categoria.nome.toLowerCase()
  const descricao = categoria.descricao?.toLowerCase() || ''
  
  if (nome.includes('imposto') || nome.includes('taxa') || nome.includes('icms') || nome.includes('ipi')) {
    return 'fiscal'
  }
  if (nome.includes('cmv') || nome.includes('depreciação') || nome.includes('provisão')) {
    return 'contabil'
  }
  if (nome.includes('financeira') || nome.includes('investimento') || nome.includes('juros')) {
    return 'financeira'
  }
  if (nome.includes('alimentação') || nome.includes('moradia') || nome.includes('transporte')) {
    return 'pessoal'
  }
  
  return 'operacional'
}

const getExpertiseColor = (expertise) => {
  const colors = {
    fiscal: 'red',
    contabil: 'blue',
    financeira: 'green',
    pessoal: 'orange',
    operacional: 'purple'
  }
  return colors[expertise] || 'grey'
}

const getExpertiseIcon = (expertise) => {
  const icons = {
    fiscal: 'mdi-gavel',
    contabil: 'mdi-calculator',
    financeira: 'mdi-chart-line',
    pessoal: 'mdi-account',
    operacional: 'mdi-cog'
  }
  return icons[expertise] || 'mdi-tag'
}

const openCreateDialog = () => {
  editingCategoria.value = null
  categoriaForm.value = {
    nome: '',
    tipo: '',
    descricao: '',
    expertise: ''
  }
  dialog.value = true
}

const editCategoria = (categoria) => {
  editingCategoria.value = categoria
  categoriaForm.value = {
    nome: categoria.nome,
    tipo: categoria.tipo,
    descricao: categoria.descricao || '',
    expertise: categoria.expertise || ''
  }
  dialog.value = true
}

const closeDialog = () => {
  dialog.value = false
  editingCategoria.value = null
  if (form.value) {
    form.value.reset()
  }
}

const saveCategoria = async () => {
  if (!formValid.value) return

  saving.value = true
  try {
    const data = { ...categoriaForm.value }
    
    if (editingCategoria.value) {
      await axios.put(`/api/v1/financeiro/categorias/${editingCategoria.value.id}`, data)
    } else {
      await axios.post('/api/v1/financeiro/categorias', data)
    }
    
    await loadCategorias()
    closeDialog()
  } catch (error) {
    console.error('Erro ao salvar categoria:', error)
  } finally {
    saving.value = false
  }
}

const confirmDelete = (categoria) => {
  categoriaToDelete.value = categoria
  deleteDialog.value = true
}

const deleteCategoria = async () => {
  if (!categoriaToDelete.value) return

  deleting.value = true
  try {
    await axios.delete(`/api/v1/financeiro/categorias/${categoriaToDelete.value.id}`)
    await loadCategorias()
    deleteDialog.value = false
    categoriaToDelete.value = null
  } catch (error) {
    console.error('Erro ao excluir categoria:', error)
  } finally {
    deleting.value = false
  }
}

const applyFilters = () => {
  // Filtros são aplicados automaticamente via computed
}

const applySuggestion = (suggestion) => {
  categoriaForm.value.nome = suggestion
}

// Lifecycle
onMounted(() => {
  loadCategorias()
})
</script>

<style lang="scss" scoped>
.categorias-page {
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
  background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%);
  min-height: 100vh;
}

// Header
.page-header {
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1.5rem;
    
    .header-info {
      .page-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: rgb(var(--v-theme-primary));
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }
      
      .page-subtitle {
        font-size: 1.1rem;
        color: rgba(var(--v-theme-on-surface), 0.7);
        font-weight: 500;
      }
    }
    
    .header-actions {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      
      .create-btn {
        background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, #1976D2 100%);
        box-shadow: 0 4px 16px rgba(var(--v-theme-primary), 0.4);
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(var(--v-theme-primary), 0.6);
        }
      }
      
      .refresh-btn {
        border-width: 2px;
        font-weight: 600;
        
        &:hover {
          transform: translateY(-1px);
        }
      }
    }
  }
}

// Cards
.filter-card, .stats-card, .categories-card {
  border-radius: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border: 1px solid rgba(var(--v-theme-primary), 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
  }
}

// Stats
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  
  .stat-item {
    text-align: center;
    
    .stat-value {
      font-size: 1.5rem;
      font-weight: 800;
      margin-bottom: 0.25rem;
    }
    
    .stat-label {
      font-size: 0.875rem;
      color: rgba(var(--v-theme-on-surface), 0.6);
      font-weight: 500;
    }
  }
}

// Tabela
.categories-table {
  .description-cell {
    max-width: 200px;
    
    .description-text {
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
  
  .action-buttons {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
  }
}

.no-data-container {
  text-align: center;
  padding: 3rem 1rem;
}

// Dialog
.dialog-card {
  border-radius: 16px;
}

.suggestions-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

// Responsividade
@media (max-width: 960px) {
  .categorias-page {
    padding: 1rem;
  }
  
  .page-header .header-content {
    flex-direction: column;
    align-items: flex-start;
    
    .header-actions {
      width: 100%;
      justify-content: flex-start;
    }
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
}

@media (max-width: 600px) {
  .header-actions {
    flex-direction: column;
    width: 100%;
    
    .v-btn {
      width: 100%;
      justify-content: center;
    }
  }
  
  .page-header .header-info .page-title {
    font-size: 2rem;
  }
}
</style> 