<template>
  <div class="biuai-metas">
    <!-- Header da página -->
    <div class="metas-header mb-6">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">
            🎯 Metas Financeiras
          </h1>
          <p class="page-subtitle">
            Defina e acompanhe seus objetivos financeiros com precisão
          </p>
        </div>
        
        <div class="header-actions">
          <v-btn
            color="primary"
            size="large"
            variant="elevated"
            prepend-icon="mdi-plus"
            @click="showNewMeta = true"
            class="new-meta-btn"
          >
            <span class="font-weight-bold">Nova Meta</span>
          </v-btn>
          
          <v-btn
            color="secondary"
            size="large"
            variant="outlined"
            :loading="loading"
            @click="carregarDados"
            class="refresh-btn"
          >
            <v-icon>mdi-refresh</v-icon>
          </v-btn>
        </div>
      </div>
    </div>

    <!-- Cards de resumo -->
    <v-row class="metrics-row mb-6">
      <v-col cols="12" md="3">
        <v-card class="metric-card metric-card--primary" elevation="8" hover>
          <v-card-text class="pa-6">
            <div class="d-flex align-center justify-space-between">
              <div class="metric-content">
                <div class="metric-icon-wrapper mb-3">
                  <v-icon icon="mdi-target" size="32" class="metric-icon" />
                </div>
                <div class="metric-label">Total de Metas</div>
                <div class="metric-value">{{ resumo.total_metas || 0 }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card class="metric-card metric-card--success" elevation="8" hover>
          <v-card-text class="pa-6">
            <div class="d-flex align-center justify-space-between">
              <div class="metric-content">
                <div class="metric-icon-wrapper mb-3">
                  <v-icon icon="mdi-play" size="32" class="metric-icon" />
                </div>
                <div class="metric-label">Metas Ativas</div>
                <div class="metric-value">{{ resumo.metas_ativas || 0 }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card class="metric-card metric-card--info" elevation="8" hover>
          <v-card-text class="pa-6">
            <div class="d-flex align-center justify-space-between">
              <div class="metric-content">
                <div class="metric-icon-wrapper mb-3">
                  <v-icon icon="mdi-check-circle" size="32" class="metric-icon" />
                </div>
                <div class="metric-label">Concluídas</div>
                <div class="metric-value">{{ resumo.metas_concluidas || 0 }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card class="metric-card metric-card--warning" elevation="8" hover>
          <v-card-text class="pa-6">
            <div class="d-flex align-center justify-space-between">
              <div class="metric-content">
                <div class="metric-icon-wrapper mb-3">
                  <v-icon icon="mdi-percent" size="32" class="metric-icon" />
                </div>
                <div class="metric-label">Progresso Geral</div>
                <div class="metric-value">{{ resumo.progresso_geral || 0 }}%</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filtros -->
    <v-card class="filters-card mb-6" elevation="2">
      <v-card-text class="pa-4">
        <v-row align="center">
          <v-col cols="12" md="4">
            <v-select
              v-model="filtros.status"
              :items="statusOptions"
              label="Status"
              density="comfortable"
              variant="outlined"
              clearable
              @update:model-value="aplicarFiltros"
            />
          </v-col>
          
          <v-col cols="12" md="4">
            <v-text-field
              v-model="pesquisaTexto"
              label="Pesquisar metas..."
              density="comfortable"
              variant="outlined"
              prepend-inner-icon="mdi-magnify"
              clearable
              @input="pesquisarMetas"
            />
          </v-col>
          
          <v-col cols="12" md="4" class="d-flex justify-end">
            <v-btn
              color="primary"
              variant="outlined"
              @click="limparFiltros"
            >
              Limpar Filtros
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-8">
      <v-progress-circular size="64" color="primary" indeterminate />
      <p class="mt-4 text-h6">Carregando metas...</p>
    </div>

    <!-- Lista de Metas -->
    <div v-else>
      <v-row>
        <v-col
          v-for="meta in metasFiltradas"
          :key="meta.id"
          cols="12"
          md="6"
          lg="4"
        >
          <v-card class="meta-card" elevation="4" hover @click="abrirDetalhesMeta(meta)">
            <v-card-title class="d-flex align-center justify-space-between pa-4">
              <span class="text-h6 font-weight-bold">{{ meta.titulo }}</span>
              <v-chip
                :color="formatarStatus(meta.status).color"
                :prepend-icon="formatarStatus(meta.status).icon"
                size="small"
                variant="elevated"
              >
                {{ formatarStatus(meta.status).label }}
              </v-chip>
            </v-card-title>

            <v-card-text class="pa-4">
              <div class="meta-info mb-4">
                <div v-if="meta.descricao" class="meta-description text-body-2 mb-3">
                  {{ meta.descricao }}
                </div>
                
                <div class="meta-valores mb-3">
                  <div class="d-flex justify-space-between mb-2">
                    <span class="text-body-2">Progresso:</span>
                    <span class="text-body-2 font-weight-bold">
                      {{ formatCurrency(meta.valor_atual) }} / {{ formatCurrency(meta.valor_meta) }}
                    </span>
                  </div>
                  
                  <v-progress-linear
                    :model-value="meta.progresso_percentual"
                    :color="getCorProgresso(meta.progresso_percentual)"
                    height="8"
                    rounded
                  />
                  
                  <div class="d-flex justify-space-between mt-2">
                    <span class="text-body-2">{{ meta.progresso_percentual }}% concluído</span>
                    <span class="text-body-2">
                      {{ meta.dias_restantes > 0 ? `${meta.dias_restantes} dias restantes` : 'Vencida' }}
                    </span>
                  </div>
                </div>

                <div v-if="meta.categoria" class="meta-categoria">
                  <v-chip size="small" color="secondary" variant="tonal">
                    {{ meta.categoria.nome }}
                  </v-chip>
                </div>
              </div>
            </v-card-text>

            <v-card-actions class="pa-4 pt-0">
              <v-btn
                color="primary"
                variant="text"
                size="small"
                prepend-icon="mdi-plus"
                @click.stop="atualizarProgressoMeta(meta)"
              >
                Adicionar Progresso
              </v-btn>
              
              <v-spacer />
              
              <v-menu>
                <template v-slot:activator="{ props }">
                  <v-btn
                    icon="mdi-dots-vertical"
                    variant="text"
                    size="small"
                    v-bind="props"
                    @click.stop
                  />
                </template>
                
                <v-list>
                  <v-list-item @click="editarMeta(meta)">
                    <v-list-item-title>
                      <v-icon icon="mdi-pencil" class="mr-2" />
                      Editar
                    </v-list-item-title>
                  </v-list-item>
                  
                  <v-list-item @click="confirmarDelecao(meta)">
                    <v-list-item-title class="text-error">
                      <v-icon icon="mdi-delete" class="mr-2" />
                      Excluir
                    </v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

      <!-- Estado vazio -->
      <div v-if="!metasFiltradas.length && !loading" class="text-center py-12">
        <v-icon icon="mdi-target" size="96" color="grey" class="mb-4" />
        <h3 class="text-h5 mb-2">Nenhuma meta encontrada</h3>
        <p class="text-body-1 mb-4">
          {{ filtros.status || pesquisaTexto ? 
            'Nenhuma meta corresponde aos filtros aplicados.' : 
            'Comece criando sua primeira meta financeira!' }}
        </p>
        <v-btn
          v-if="!filtros.status && !pesquisaTexto"
          color="primary"
          variant="elevated"
          prepend-icon="mdi-plus"
          @click="showNewMeta = true"
        >
          Criar Primeira Meta
        </v-btn>
      </div>
    </div>

    <!-- Dialog Nova/Editar Meta -->
    <v-dialog v-model="showNewMeta" max-width="600" persistent>
      <v-card>
        <v-card-title class="text-h5 pa-6">
          <v-icon icon="mdi-target" class="mr-3" />
          {{ metaEditando ? 'Editar Meta' : 'Nova Meta Financeira' }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-form ref="formMeta" v-model="formValido">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="formMeta.titulo"
                  label="Título da Meta *"
                  variant="outlined"
                  :rules="[v => !!v || 'Título é obrigatório']"
                  prepend-inner-icon="mdi-format-title"
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="formMeta.descricao"
                  label="Descrição (opcional)"
                  variant="outlined"
                  rows="3"
                  prepend-inner-icon="mdi-text"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="formMeta.valor_meta"
                  label="Valor da Meta *"
                  variant="outlined"
                  type="number"
                  prefix="R$"
                  :rules="[
                    v => !!v || 'Valor é obrigatório',
                    v => v > 0 || 'Valor deve ser maior que zero'
                  ]"
                  prepend-inner-icon="mdi-currency-usd"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="formMeta.valor_atual"
                  label="Valor Atual"
                  variant="outlined"
                  type="number"
                  prefix="R$"
                  :rules="[v => v >= 0 || 'Valor deve ser positivo']"
                  prepend-inner-icon="mdi-cash"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formMeta.data_inicio"
                  label="Data de Início *"
                  variant="outlined"
                  type="date"
                  :rules="[v => !!v || 'Data de início é obrigatória']"
                  prepend-inner-icon="mdi-calendar-start"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formMeta.data_fim"
                  label="Data de Fim *"
                  variant="outlined"
                  type="date"
                  :rules="[
                    v => !!v || 'Data de fim é obrigatória',
                    v => !formMeta.data_inicio || new Date(v) > new Date(formMeta.data_inicio) || 'Data deve ser posterior ao início'
                  ]"
                  prepend-inner-icon="mdi-calendar-end"
                />
              </v-col>

              <v-col cols="12">
                <v-select
                  v-model="formMeta.categoria_id"
                  :items="categorias"
                  item-title="nome"
                  item-value="id"
                  label="Categoria (opcional)"
                  variant="outlined"
                  clearable
                  prepend-inner-icon="mdi-tag"
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-card-actions class="pa-6">
          <v-spacer />
          <v-btn
            variant="text"
            @click="cancelarFormulario"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :loading="salvando"
            :disabled="!formValido"
            @click="salvarMeta"
          >
            {{ metaEditando ? 'Atualizar' : 'Criar Meta' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog Atualizar Progresso -->
    <v-dialog v-model="showProgressoDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6 pa-6">
          Atualizar Progresso
        </v-card-title>

        <v-card-text class="pa-6">
          <v-text-field
            v-model.number="novoValorProgresso"
            label="Novo Valor Atual"
            variant="outlined"
            type="number"
            prefix="R$"
            :rules="[v => v >= 0 || 'Valor deve ser positivo']"
          />
        </v-card-text>

        <v-card-actions class="pa-6">
          <v-spacer />
          <v-btn variant="text" @click="showProgressoDialog = false">
            Cancelar
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :loading="salvandoProgresso"
            @click="salvarProgresso"
          >
            Atualizar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog Confirmação de Deleção -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6 pa-6">
          Confirmar Exclusão
        </v-card-title>

        <v-card-text class="pa-6">
          Tem certeza que deseja excluir a meta "{{ metaParaDeletar?.titulo }}"?
          Esta ação não pode ser desfeita.
        </v-card-text>

        <v-card-actions class="pa-6">
          <v-spacer />
          <v-btn variant="text" @click="showDeleteDialog = false">
            Cancelar
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            :loading="deletando"
            @click="deletarMeta"
          >
            Excluir
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { metasService } from '@/services/metas'
import { api } from '@/boot/axios'

export default {
  name: 'MetasPage',
  setup() {

    // Estados reativos
    const loading = ref(false)
    const salvando = ref(false)
    const salvandoProgresso = ref(false)
    const deletando = ref(false)
    const showNewMeta = ref(false)
    const showProgressoDialog = ref(false)
    const showDeleteDialog = ref(false)
    const formValido = ref(false)
    const pesquisaTexto = ref('')
    
    const metas = ref([])
    const categorias = ref([])
    const resumo = ref({})
    const metaEditando = ref(null)
    const metaParaDeletar = ref(null)
    const metaParaProgresso = ref(null)
    const novoValorProgresso = ref(0)

    const filtros = reactive({
      status: ''
    })

    const formMeta = reactive({
      titulo: '',
      descricao: '',
      valor_meta: null,
      valor_atual: 0,
      data_inicio: '',
      data_fim: '',
      categoria_id: null
    })

    // Computed
    const statusOptions = computed(() => metasService.getStatusOptions())
    
    const metasFiltradas = computed(() => {
      let resultado = metas.value

      if (filtros.status) {
        resultado = resultado.filter(meta => meta.status === filtros.status)
      }

      if (pesquisaTexto.value) {
        const termo = pesquisaTexto.value.toLowerCase()
        resultado = resultado.filter(meta => 
          meta.titulo.toLowerCase().includes(termo) ||
          (meta.descricao && meta.descricao.toLowerCase().includes(termo))
        )
      }

      return resultado
    })

    // Métodos
    const carregarDados = async () => {
      loading.value = true
      try {
        const [metasData, categoriasResponse, resumoData] = await Promise.all([
          metasService.listarMetas(),
          api.get('/api/v1/financeiro/categorias'),
          metasService.obterResumoEstatisticas()
        ])
        
        const categoriasData = categoriasResponse.data
        
        metas.value = metasData
        categorias.value = categoriasData
        resumo.value = resumoData
      } catch (error) {
        console.error('Erro ao carregar dados:', error)
        console.error('Erro ao carregar dados das metas')
      } finally {
        loading.value = false
      }
    }

    const salvarMeta = async () => {
      salvando.value = true
      try {
        if (metaEditando.value) {
          await metasService.atualizarMeta(metaEditando.value.id, formMeta)
          console.log('Meta atualizada com sucesso!')
        } else {
          await metasService.criarMeta(formMeta)
          console.log('Meta criada com sucesso!')
        }
        
        cancelarFormulario()
        await carregarDados()
      } catch (error) {
        console.error('Erro ao salvar meta:', error)
        console.error('Erro ao salvar meta')
      } finally {
        salvando.value = false
      }
    }

    const editarMeta = (meta) => {
      metaEditando.value = meta
      Object.assign(formMeta, {
        titulo: meta.titulo,
        descricao: meta.descricao,
        valor_meta: meta.valor_meta,
        valor_atual: meta.valor_atual,
        data_inicio: meta.data_inicio?.split('T')[0],
        data_fim: meta.data_fim?.split('T')[0],
        categoria_id: meta.categoria_id
      })
      showNewMeta.value = true
    }

    const atualizarProgressoMeta = (meta) => {
      metaParaProgresso.value = meta
      novoValorProgresso.value = meta.valor_atual
      showProgressoDialog.value = true
    }

    const salvarProgresso = async () => {
      salvandoProgresso.value = true
      try {
        await metasService.atualizarValorMeta(
          metaParaProgresso.value.id, 
          novoValorProgresso.value
        )
        
        console.log('Progresso atualizado com sucesso!')
        
        showProgressoDialog.value = false
        await carregarDados()
      } catch (error) {
        console.error('Erro ao atualizar progresso:', error)
        console.error('Erro ao atualizar progresso')
      } finally {
        salvandoProgresso.value = false
      }
    }

    const confirmarDelecao = (meta) => {
      metaParaDeletar.value = meta
      showDeleteDialog.value = true
    }

    const deletarMeta = async () => {
      deletando.value = true
      try {
        await metasService.deletarMeta(metaParaDeletar.value.id)
        console.log('Meta excluída com sucesso!')
        
        showDeleteDialog.value = false
        await carregarDados()
      } catch (error) {
        console.error('Erro ao deletar meta:', error)
        console.error('Erro ao excluir meta')
      } finally {
        deletando.value = false
      }
    }

    const cancelarFormulario = () => {
      showNewMeta.value = false
      metaEditando.value = null
      Object.assign(formMeta, {
        titulo: '',
        descricao: '',
        valor_meta: null,
        valor_atual: 0,
        data_inicio: '',
        data_fim: '',
        categoria_id: null
      })
    }

    const aplicarFiltros = () => {
      // Filtros são aplicados automaticamente via computed
    }

    const limparFiltros = () => {
      filtros.status = ''
      pesquisaTexto.value = ''
    }

    const pesquisarMetas = () => {
      // Pesquisa é aplicada automaticamente via computed
    }

    const abrirDetalhesMeta = (meta) => {
      // Implementar modal de detalhes se necessário
      console.log('Abrir detalhes da meta:', meta)
    }

    // Formatadores
    const formatCurrency = (value) => {
      if (!value) return 'R$ 0,00'
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      }).format(value)
    }

    const formatarStatus = (status) => metasService.formatarStatus(status)
    
    const getCorProgresso = (progresso) => metasService.getCorProgresso(progresso)

    // Lifecycle
    onMounted(() => {
      carregarDados()
    })

    return {
      // Estados
      loading,
      salvando,
      salvandoProgresso,
      deletando,
      showNewMeta,
      showProgressoDialog,
      showDeleteDialog,
      formValido,
      pesquisaTexto,
      metas,
      categorias,
      resumo,
      metaEditando,
      metaParaDeletar,
      metaParaProgresso,
      novoValorProgresso,
      filtros,
      formMeta,
      
      // Computed
      statusOptions,
      metasFiltradas,
      
      // Métodos
      carregarDados,
      salvarMeta,
      editarMeta,
      atualizarProgressoMeta,
      salvarProgresso,
      confirmarDelecao,
      deletarMeta,
      cancelarFormulario,
      aplicarFiltros,
      limparFiltros,
      pesquisarMetas,
      abrirDetalhesMeta,
      formatCurrency,
      formatarStatus,
      getCorProgresso
    }
  }
}
</script>

<style scoped>
.biuai-metas {
  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.metas-header {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 24px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1976D2;
  margin: 0;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #666;
  margin: 8px 0 0 0;
}

.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.metrics-row .metric-card {
  border-radius: 16px;
  background: linear-gradient(135deg, var(--v-theme-primary) 0%, var(--v-theme-primary-darken-1) 100%);
  color: white;
  transition: transform 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-4px);
}

.metric-card--primary {
  background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
}

.metric-card--success {
  background: linear-gradient(135deg, #43A047 0%, #388E3C 100%);
}

.metric-card--info {
  background: linear-gradient(135deg, #00ACC1 0%, #0097A7 100%);
}

.metric-card--warning {
  background: linear-gradient(135deg, #FB8C00 0%, #F57C00 100%);
}

.metric-icon-wrapper {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.metric-label {
  font-size: 0.9rem;
  opacity: 0.9;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 2rem;
  font-weight: bold;
}

.filters-card {
  border-radius: 12px;
}

.meta-card {
  border-radius: 16px;
  transition: all 0.3s ease;
  height: 100%;
  cursor: pointer;
}

.meta-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.meta-description {
  color: #666;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.meta-valores {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
}

@media (max-width: 960px) {
  .biuai-metas {
    padding: 16px;
  }
  
  .metas-header {
    padding: 24px;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style> 