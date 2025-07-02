<template>
  <div class="biuai-contas">
    <!-- Header da página -->
    <div class="contas-header mb-6">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">
            🏦 Contas Bancárias
          </h1>
          <p class="page-subtitle">
            Gerencie suas contas e acompanhe saldos em tempo real
          </p>
        </div>
        
        <div class="header-actions">
          <v-btn
            color="primary"
            size="large"
            variant="elevated"
            prepend-icon="mdi-plus"
            @click="showNewConta = true"
            class="new-conta-btn"
          >
            <span class="font-weight-bold">Nova Conta</span>
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
                  <v-icon icon="mdi-bank" size="32" class="metric-icon" />
                </div>
                <div class="metric-label">Total de Contas</div>
                <div class="metric-value">{{ resumo.total_contas || 0 }}</div>
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
                  <v-icon icon="mdi-check-circle" size="32" class="metric-icon" />
                </div>
                <div class="metric-label">Contas Ativas</div>
                <div class="metric-value">{{ resumo.contas_ativas || 0 }}</div>
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
                  <v-icon icon="mdi-cash" size="32" class="metric-icon" />
                </div>
                <div class="metric-label">Saldo Total</div>
                <div class="metric-value">{{ formatarSaldo(resumo.saldo_total) }}</div>
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
                  <v-icon icon="mdi-office-building" size="32" class="metric-icon" />
                </div>
                <div class="metric-label">Banco Principal</div>
                <div class="metric-value text-caption">{{ resumo.banco_principal || 'N/A' }}</div>
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
          <v-col cols="12" md="3">
            <v-select
              v-model="filtros.ativa"
              :items="statusOptions"
              label="Status"
              density="comfortable"
              variant="outlined"
              clearable
              @update:model-value="aplicarFiltros"
            />
          </v-col>
          
          <v-col cols="12" md="3">
            <v-select
              v-model="filtros.tipo_conta"
              :items="tiposContaOptions"
              label="Tipo de Conta"
              density="comfortable"
              variant="outlined"
              clearable
              @update:model-value="aplicarFiltros"
            />
          </v-col>
          
          <v-col cols="12" md="3">
            <v-text-field
              v-model="pesquisaTexto"
              label="Pesquisar contas..."
              density="comfortable"
              variant="outlined"
              prepend-inner-icon="mdi-magnify"
              clearable
              @input="pesquisarContas"
            />
          </v-col>
          
          <v-col cols="12" md="3" class="d-flex justify-end">
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
      <p class="mt-4 text-h6">Carregando contas...</p>
    </div>

    <!-- Lista de Contas -->
    <div v-else>
      <!-- Agrupamento por Banco -->
      <div v-for="(contasBanco, banco) in contasAgrupadasPorBanco" :key="banco" class="mb-6">
        <v-card class="banco-group-card" elevation="2">
          <v-card-title class="pa-4 bank-header">
            <div class="d-flex align-center justify-space-between w-100">
              <div class="d-flex align-center">
                <v-icon icon="mdi-office-building" class="mr-3" />
                <span class="text-h6 font-weight-bold">{{ banco }}</span>
                <v-chip class="ml-3" size="small" color="primary" variant="tonal">
                  {{ contasBanco.length }} {{ contasBanco.length === 1 ? 'conta' : 'contas' }}
                </v-chip>
              </div>
              <div class="text-h6 font-weight-bold">
                {{ formatarSaldo(calcularSaldoBanco(contasBanco)) }}
              </div>
            </div>
          </v-card-title>

          <v-card-text class="pa-0">
            <v-row class="ma-0">
              <v-col
                v-for="conta in contasBanco"
                :key="conta.id"
                cols="12"
                md="6"
                lg="4"
                class="pa-2"
              >
                <v-card 
                  class="conta-card" 
                  elevation="4" 
                  hover 
                  @click="abrirDetalhesConta(conta)"
                  :class="{ 'conta-inativa': conta.ativa !== 'true' }"
                >
                  <v-card-title class="pa-4 pb-2">
                    <div class="d-flex align-center justify-space-between w-100">
                      <div class="d-flex align-center">
                        <v-icon 
                          :icon="formatarTipoConta(conta.tipo_conta).icon" 
                          :color="formatarTipoConta(conta.tipo_conta).color"
                          class="mr-2"
                        />
                        <span class="text-h6 font-weight-bold">{{ conta.nome }}</span>
                      </div>
                      <v-chip
                        :color="formatarStatusConta(conta.ativa).color"
                        :prepend-icon="formatarStatusConta(conta.ativa).icon"
                        size="small"
                        variant="elevated"
                      >
                        {{ formatarStatusConta(conta.ativa).label }}
                      </v-chip>
                    </div>
                  </v-card-title>

                  <v-card-text class="pa-4">
                    <div class="conta-info">
                      <div class="conta-detalhes mb-3">
                        <div class="text-body-2 mb-1">
                          <strong>Tipo:</strong> {{ formatarTipoConta(conta.tipo_conta).label }}
                        </div>
                        <div v-if="conta.numero_conta" class="text-body-2 mb-1">
                          <strong>Conta:</strong> {{ formatarNumeroConta(conta.numero_conta, conta.agencia) }}
                        </div>
                      </div>

                      <div class="saldo-info">
                        <v-card 
                          class="saldo-card pa-3" 
                          :color="getCorSaldo(conta.saldo_atual)"
                          variant="tonal"
                        >
                          <div class="text-center">
                            <div class="text-body-2 mb-1">Saldo Atual</div>
                            <div class="text-h6 font-weight-bold">
                              {{ formatarSaldo(conta.saldo_atual) }}
                            </div>
                          </div>
                        </v-card>
                      </div>

                      <div v-if="conta.total_lancamentos > 0" class="estatisticas-conta mt-3">
                        <v-row dense>
                          <v-col cols="4" class="text-center">
                            <div class="text-caption">Lançamentos</div>
                            <div class="text-body-2 font-weight-bold">{{ conta.total_lancamentos }}</div>
                          </v-col>
                          <v-col cols="4" class="text-center">
                            <div class="text-caption text-success">Receitas</div>
                            <div class="text-body-2 font-weight-bold text-success">
                              {{ formatarSaldo(conta.total_receitas) }}
                            </div>
                          </v-col>
                          <v-col cols="4" class="text-center">
                            <div class="text-caption text-error">Despesas</div>
                            <div class="text-body-2 font-weight-bold text-error">
                              {{ formatarSaldo(conta.total_despesas) }}
                            </div>
                          </v-col>
                        </v-row>
                      </div>
                    </div>
                  </v-card-text>

                  <v-card-actions class="pa-4 pt-0">
                    <v-btn
                      color="primary"
                      variant="text"
                      size="small"
                      prepend-icon="mdi-eye"
                      @click.stop="verLancamentosConta(conta)"
                    >
                      Ver Lançamentos
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
                        <v-list-item @click="editarConta(conta)">
                          <v-list-item-title>
                            <v-icon icon="mdi-pencil" class="mr-2" />
                            Editar
                          </v-list-item-title>
                        </v-list-item>
                        
                        <v-list-item @click="alterarStatusConta(conta)">
                          <v-list-item-title :class="conta.ativa === 'true' ? 'text-warning' : 'text-success'">
                            <v-icon :icon="conta.ativa === 'true' ? 'mdi-pause' : 'mdi-play'" class="mr-2" />
                            {{ conta.ativa === 'true' ? 'Desativar' : 'Ativar' }}
                          </v-list-item-title>
                        </v-list-item>
                        
                        <v-list-item @click="confirmarDelecao(conta)">
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
          </v-card-text>
        </v-card>
      </div>

      <!-- Estado vazio -->
      <div v-if="!contasFiltradas.length && !loading" class="text-center py-12">
        <v-icon icon="mdi-bank" size="96" color="grey" class="mb-4" />
        <h3 class="text-h5 mb-2">Nenhuma conta encontrada</h3>
        <p class="text-body-1 mb-4">
          {{ filtros.ativa || filtros.tipo_conta || pesquisaTexto ? 
            'Nenhuma conta corresponde aos filtros aplicados.' : 
            'Comece adicionando sua primeira conta bancária!' }}
        </p>
        <v-btn
          v-if="!filtros.ativa && !filtros.tipo_conta && !pesquisaTexto"
          color="primary"
          variant="elevated"
          prepend-icon="mdi-plus"
          @click="showNewConta = true"
        >
          Adicionar Primeira Conta
        </v-btn>
      </div>
    </div>

    <!-- Dialog Nova/Editar Conta -->
    <v-dialog v-model="showNewConta" max-width="700" persistent>
      <v-card>
        <v-card-title class="text-h5 pa-6">
          <v-icon icon="mdi-bank" class="mr-3" />
          {{ contaEditando ? 'Editar Conta' : 'Nova Conta Bancária' }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-form ref="formConta" v-model="formValido">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formConta.nome"
                  label="Nome da Conta *"
                  variant="outlined"
                  :rules="[v => !!v || 'Nome é obrigatório']"
                  prepend-inner-icon="mdi-format-title"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-combobox
                  v-model="formConta.banco"
                  :items="bancosComuns"
                  label="Banco *"
                  variant="outlined"
                  :rules="[v => !!v || 'Banco é obrigatório']"
                  prepend-inner-icon="mdi-office-building"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-select
                  v-model="formConta.tipo_conta"
                  :items="tiposContaOptions.filter(t => t.value)"
                  label="Tipo de Conta *"
                  variant="outlined"
                  :rules="[v => !!v || 'Tipo é obrigatório']"
                  prepend-inner-icon="mdi-credit-card"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="formConta.saldo_inicial"
                  label="Saldo Inicial *"
                  variant="outlined"
                  type="number"
                  prefix="R$"
                  step="0.01"
                  :rules="[v => v !== null && v !== undefined || 'Saldo inicial é obrigatório']"
                  prepend-inner-icon="mdi-cash"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formConta.agencia"
                  label="Agência (opcional)"
                  variant="outlined"
                  prepend-inner-icon="mdi-bank-outline"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formConta.numero_conta"
                  label="Número da Conta (opcional)"
                  variant="outlined"
                  prepend-inner-icon="mdi-credit-card-outline"
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
            @click="salvarConta"
          >
            {{ contaEditando ? 'Atualizar' : 'Criar Conta' }}
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
          Tem certeza que deseja excluir a conta "{{ contaParaDeletar?.nome }}" do {{ contaParaDeletar?.banco }}?
          Esta ação irá desvincular todos os lançamentos da conta, mas não os excluirá.
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
            @click="deletarConta"
          >
            Excluir
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog Lançamentos da Conta -->
    <v-dialog v-model="showLancamentosDialog" max-width="900">
      <v-card>
        <v-card-title class="text-h6 pa-6">
          Lançamentos - {{ contaSelecionada?.nome }} ({{ contaSelecionada?.banco }})
        </v-card-title>

        <v-card-text class="pa-6">
          <div v-if="loadingLancamentos" class="text-center py-4">
            <v-progress-circular size="32" color="primary" indeterminate />
            <p class="mt-2">Carregando lançamentos...</p>
          </div>

          <div v-else-if="lancamentosConta.length">
            <v-list>
              <v-list-item
                v-for="lancamento in lancamentosConta"
                :key="lancamento.id"
                class="mb-2"
              >
                <template v-slot:prepend>
                  <v-icon 
                    :icon="lancamento.tipo === 'RECEITA' ? 'mdi-trending-up' : 'mdi-trending-down'"
                    :color="lancamento.tipo === 'RECEITA' ? 'success' : 'error'"
                  />
                </template>

                <v-list-item-title>{{ lancamento.descricao }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ new Date(lancamento.data_lancamento).toLocaleDateString('pt-BR') }}
                </v-list-item-subtitle>

                <template v-slot:append>
                  <v-chip 
                    :color="lancamento.tipo === 'RECEITA' ? 'success' : 'error'"
                    variant="elevated"
                  >
                    {{ formatarSaldo(lancamento.valor) }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </div>

          <div v-else class="text-center py-8">
            <v-icon icon="mdi-inbox" size="64" color="grey" />
            <p class="mt-2 text-body-1">Nenhum lançamento encontrado para esta conta</p>
          </div>
        </v-card-text>

        <v-card-actions class="pa-6">
          <v-spacer />
          <v-btn variant="text" @click="showLancamentosDialog = false">
            Fechar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { contasService } from '@/services/contas'

export default {
  name: 'ContasPage',
  setup() {

    // Estados reativos
    const loading = ref(false)
    const loadingLancamentos = ref(false)
    const salvando = ref(false)
    const deletando = ref(false)
    const showNewConta = ref(false)
    const showDeleteDialog = ref(false)
    const showLancamentosDialog = ref(false)
    const formValido = ref(false)
    const pesquisaTexto = ref('')
    
    const contas = ref([])
    const resumo = ref({})
    const contaEditando = ref(null)
    const contaParaDeletar = ref(null)
    const contaSelecionada = ref(null)
    const lancamentosConta = ref([])

    const filtros = reactive({
      ativa: '',
      tipo_conta: ''
    })

    const formConta = reactive({
      nome: '',
      banco: '',
      tipo_conta: 'CORRENTE',
      numero_conta: '',
      agencia: '',
      saldo_inicial: 0
    })

    // Computed
    const statusOptions = computed(() => contasService.getStatusOptions())
    const tiposContaOptions = computed(() => contasService.getTiposContaOptions())
    const bancosComuns = computed(() => contasService.getBancosComuns())
    
    const contasFiltradas = computed(() => {
      let resultado = contas.value

      if (filtros.ativa) {
        resultado = resultado.filter(conta => conta.ativa === filtros.ativa)
      }

      if (filtros.tipo_conta) {
        resultado = resultado.filter(conta => conta.tipo_conta === filtros.tipo_conta)
      }

      if (pesquisaTexto.value) {
        const termo = pesquisaTexto.value.toLowerCase()
        resultado = resultado.filter(conta => 
          conta.nome.toLowerCase().includes(termo) ||
          conta.banco.toLowerCase().includes(termo) ||
          (conta.numero_conta && conta.numero_conta.toLowerCase().includes(termo))
        )
      }

      return resultado
    })

    const contasAgrupadasPorBanco = computed(() => {
      return contasService.agruparPorBanco(contasFiltradas.value)
    })

    // Métodos
    const carregarDados = async () => {
      loading.value = true
      try {
        const [contasData, resumoData] = await Promise.all([
          contasService.listarContas(),
          contasService.obterResumoEstatisticas()
        ])
        
        contas.value = contasData
        resumo.value = resumoData
      } catch (error) {
        console.error('Erro ao carregar dados:', error)
        console.error('Erro ao carregar dados das contas')
      } finally {
        loading.value = false
      }
    }

    const salvarConta = async () => {
      salvando.value = true
      try {
        if (contaEditando.value) {
          await contasService.atualizarConta(contaEditando.value.id, formConta)
          console.log('Conta atualizada com sucesso!')
        } else {
          await contasService.criarConta(formConta)
          console.log('Conta criada com sucesso!')
        }
        
        cancelarFormulario()
        await carregarDados()
      } catch (error) {
        console.error('Erro ao salvar conta:', error)
        console.error('Erro ao salvar conta')
      } finally {
        salvando.value = false
      }
    }

    const editarConta = (conta) => {
      contaEditando.value = conta
      Object.assign(formConta, {
        nome: conta.nome,
        banco: conta.banco,
        tipo_conta: conta.tipo_conta,
        numero_conta: conta.numero_conta || '',
        agencia: conta.agencia || '',
        saldo_inicial: conta.saldo_inicial
      })
      showNewConta.value = true
    }

    const alterarStatusConta = async (conta) => {
      try {
        const ativar = conta.ativa !== 'true'
        await contasService.alterarStatusConta(conta.id, ativar)
        
        console.log(`Conta ${ativar ? 'ativada' : 'desativada'} com sucesso!`)
        
        await carregarDados()
      } catch (error) {
        console.error('Erro ao alterar status da conta:', error)
        console.error('Erro ao alterar status da conta')
      }
    }

    const confirmarDelecao = (conta) => {
      contaParaDeletar.value = conta
      showDeleteDialog.value = true
    }

    const deletarConta = async () => {
      deletando.value = true
      try {
        await contasService.deletarConta(contaParaDeletar.value.id)
        console.log('Conta excluída com sucesso!')
        
        showDeleteDialog.value = false
        await carregarDados()
      } catch (error) {
        console.error('Erro ao deletar conta:', error)
        console.error('Erro ao excluir conta')
      } finally {
        deletando.value = false
      }
    }

    const verLancamentosConta = async (conta) => {
      contaSelecionada.value = conta
      showLancamentosDialog.value = true
      loadingLancamentos.value = true
      
      try {
        const response = await contasService.listarLancamentosConta(conta.id, { limit: 50 })
        lancamentosConta.value = response.lancamentos || []
      } catch (error) {
        console.error('Erro ao carregar lançamentos da conta:', error)
        $q.notify({
          type: 'negative',
          message: 'Erro ao carregar lançamentos da conta'
        })
        lancamentosConta.value = []
      } finally {
        loadingLancamentos.value = false
      }
    }

    const cancelarFormulario = () => {
      showNewConta.value = false
      contaEditando.value = null
      Object.assign(formConta, {
        nome: '',
        banco: '',
        tipo_conta: 'CORRENTE',
        numero_conta: '',
        agencia: '',
        saldo_inicial: 0
      })
    }

    const aplicarFiltros = () => {
      // Filtros são aplicados automaticamente via computed
    }

    const limparFiltros = () => {
      filtros.ativa = ''
      filtros.tipo_conta = ''
      pesquisaTexto.value = ''
    }

    const pesquisarContas = () => {
      // Pesquisa é aplicada automaticamente via computed
    }

    const abrirDetalhesConta = (conta) => {
      // Implementar modal de detalhes se necessário
      console.log('Abrir detalhes da conta:', conta)
    }

    // Utilitários
    const calcularSaldoBanco = (contasBanco) => {
      return contasBanco
        .filter(conta => conta.ativa === 'true')
        .reduce((total, conta) => total + (conta.saldo_atual || 0), 0)
    }

    // Formatadores
    const formatarSaldo = (valor) => contasService.formatarSaldo(valor)
    const formatarTipoConta = (tipo) => contasService.formatarTipoConta(tipo)
    const formatarStatusConta = (ativa) => contasService.formatarStatusConta(ativa)
    const formatarNumeroConta = (numero, agencia) => contasService.formatarNumeroConta(numero, agencia)
    const getCorSaldo = (saldo) => contasService.getCorSaldo(saldo)

    // Lifecycle
    onMounted(() => {
      carregarDados()
    })

    return {
      // Estados
      loading,
      loadingLancamentos,
      salvando,
      deletando,
      showNewConta,
      showDeleteDialog,
      showLancamentosDialog,
      formValido,
      pesquisaTexto,
      contas,
      resumo,
      contaEditando,
      contaParaDeletar,
      contaSelecionada,
      lancamentosConta,
      filtros,
      formConta,
      
      // Computed
      statusOptions,
      tiposContaOptions,
      bancosComuns,
      contasFiltradas,
      contasAgrupadasPorBanco,
      
      // Métodos
      carregarDados,
      salvarConta,
      editarConta,
      alterarStatusConta,
      confirmarDelecao,
      deletarConta,
      verLancamentosConta,
      cancelarFormulario,
      aplicarFiltros,
      limparFiltros,
      pesquisarContas,
      abrirDetalhesConta,
      calcularSaldoBanco,
      formatarSaldo,
      formatarTipoConta,
      formatarStatusConta,
      formatarNumeroConta,
      getCorSaldo
    }
  }
}
</script>

<style scoped>
.biuai-contas {
  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.contas-header {
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

.banco-group-card {
  border-radius: 16px;
  margin-bottom: 24px;
}

.bank-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 16px 16px 0 0;
}

.conta-card {
  border-radius: 16px;
  transition: all 0.3s ease;
  height: 100%;
  cursor: pointer;
}

.conta-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.conta-inativa {
  opacity: 0.7;
}

.conta-inativa .conta-card {
  border: 2px dashed #ccc;
}

.saldo-card {
  border-radius: 12px;
}

.estatisticas-conta {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 8px;
}

@media (max-width: 960px) {
  .biuai-contas {
    padding: 16px;
  }
  
  .contas-header {
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