<template>
  <div class="fii-dashboard">
    <!-- Cabeçalho -->
    <PageHeader
      title="Dashboard de FIIs"
      subtitle="Gestão e análise dos seus Fundos de Investimento Imobiliário"
      icon="mdi-office-building"
      :breadcrumbs="[
        { title: 'Home', to: '/' },
        { title: 'Dashboard de FIIs', disabled: true }
      ]"
    >
      <template #actions>
        <AddFIIDialog @fii-added="carregarDados" />
      </template>

      <template #metrics>
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Total Investido"
              :value="totalInvestido"
              icon="mdi-cash"
              color="primary"
              format="currency"
              :trend="{ value: crescimentoPatrimonio, type: crescimentoPatrimonio >= 0 ? 'up' : 'down' }"
            />
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Dividend Yield Médio"
              :value="dyMedio"
              icon="mdi-chart-line"
              color="success"
              format="percentage"
              :trend="{ value: crescimentoDY, type: crescimentoDY >= 0 ? 'up' : 'down' }"
            />
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Total de FIIs"
              :value="totalFIIs"
              icon="mdi-office-building-marker"
              color="info"
            />
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Proventos no Mês"
              :value="proventosMes"
              icon="mdi-cash-multiple"
              color="warning"
              format="currency"
              :trend="{ value: crescimentoProventos, type: crescimentoProventos >= 0 ? 'up' : 'down' }"
            />
          </v-col>
        </v-row>
      </template>
    </PageHeader>

    <!-- Conteúdo Principal -->
    <v-row>
      <!-- Lista de FIIs -->
      <v-col cols="12" lg="8">
        <v-card>
          <v-card-title class="d-flex align-center pa-4">
            <span class="text-h6">Meus FIIs</span>
            <v-spacer />
            
            <!-- Filtros -->
            <v-text-field
              v-model="search"
              append-icon="mdi-magnify"
              label="Buscar"
              hide-details
              density="compact"
              class="ml-4"
              style="max-width: 200px"
            />
            
            <v-select
              v-model="filtroSegmento"
              :items="segmentos"
              label="Segmento"
              hide-details
              density="compact"
              class="ml-4"
              style="max-width: 150px"
              clearable
            />
          </v-card-title>

          <v-data-table
            :headers="headers"
            :items="fiisFiltrados"
            :loading="loading"
            :search="search"
            hover
          >
            <!-- Código -->
            <template v-slot:item.codigo="{ item }">
              <div class="d-flex align-center">
                <v-icon
                  :icon="item.raw.favorito ? 'mdi-star' : 'mdi-star-outline'"
                  :color="item.raw.favorito ? 'warning' : 'grey'"
                  class="mr-2"
                  size="small"
                  @click="alternarFavorito(item.raw.id)"
                />
                {{ item.raw.codigo }}
              </div>
            </template>

            <!-- Preço Atual -->
            <template v-slot:item.preco_atual="{ item }">
              {{ formatCurrency(item.raw.preco_atual) }}
            </template>

            <!-- Dividend Yield -->
            <template v-slot:item.dividend_yield="{ item }">
              <v-chip
                :color="getDYColor(item.raw.dividend_yield)"
                size="small"
                variant="tonal"
              >
                {{ formatPercentage(item.raw.dividend_yield) }}
              </v-chip>
            </template>

            <!-- Liquidez -->
            <template v-slot:item.liquidez_diaria="{ item }">
              {{ formatCurrency(item.raw.liquidez_diaria) }}
            </template>

            <!-- Ações -->
            <template v-slot:item.actions="{ item }">
              <div class="d-flex gap-2">
                <v-btn
                  icon="mdi-pencil"
                  variant="text"
                  size="small"
                  color="primary"
                  @click="editarFII(item.raw)"
                />
                <v-btn
                  icon="mdi-delete"
                  variant="text"
                  size="small"
                  color="error"
                  @click="confirmarRemocao(item.raw)"
                />
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-col>

      <!-- Análises e Insights -->
      <v-col cols="12" lg="4">
        <!-- Distribuição por Segmento -->
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center pa-4">
            <v-icon icon="mdi-chart-pie" color="primary" class="mr-2" />
            Distribuição por Segmento
          </v-card-title>
          <v-card-text>
            <v-chart :option="chartOptions" autoresize />
          </v-card-text>
        </v-card>

        <!-- Insights da IA -->
        <MCPWidget
          title="Insights da IA"
          subtitle="Análises e recomendações inteligentes"
          icon="mdi-brain"
          type="list"
          :items="insights"
          :loading="loadingInsights"
          :action-button="{
            text: 'Ver Análise Completa',
            icon: 'mdi-chart-box',
            variant: 'tonal'
          }"
          @action="verAnaliseCompleta"
        />
      </v-col>
    </v-row>

    <!-- Diálogo de Edição -->
    <EditFIIDialog
      v-model="showEditDialog"
      :fii="fiiSelecionado"
      @fii-updated="carregarDados"
    />

    <!-- Diálogo de Confirmação -->
    <v-dialog v-model="showConfirmDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">
          Confirmar Remoção
        </v-card-title>
        <v-card-text>
          Tem certeza que deseja remover o FII {{ fiiSelecionado?.codigo }}?
          Esta ação não pode ser desfeita.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            color="grey-darken-1"
            variant="text"
            @click="showConfirmDialog = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="error"
            variant="text"
            :loading="loading"
            @click="removerFIISelecionado"
          >
            Remover
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import MetricCard from '@/components/base/MetricCard.vue'
import PageHeader from '@/components/base/PageHeader.vue'
import MCPWidget from '@/components/MCPWidget.vue'
import AddFIIDialog from '@/components/modals/AddFIIDialog.vue'
import EditFIIDialog from '@/components/modals/EditFIIDialog.vue'
import { useFIIs } from '@/composables/useFIIs'
import { computed, onMounted, ref } from 'vue'
import VChart from 'vue-echarts'
import { useRouter } from 'vue-router'

// Composables
const router = useRouter()
const {
  fiis,
  loading,
  totalInvestido,
  dyMedio,
  segmentos,
  carregarFIIs,
  alternarFavorito: toggleFavorito,
  removerFII
} = useFIIs()

// Estado local
const search = ref('')
const filtroSegmento = ref(null)
const showEditDialog = ref(false)
const showConfirmDialog = ref(false)
const fiiSelecionado = ref(null)
const loadingInsights = ref(false)
const insights = ref([])

// Dados computados
const fiisFiltrados = computed(() => {
  let resultado = [...fiis.value]
  
  if (filtroSegmento.value) {
    resultado = resultado.filter(fii => fii.segmento === filtroSegmento.value)
  }
  
  return resultado
})

const totalFIIs = computed(() => fiis.value.length)

const proventosMes = computed(() => {
  return fiis.value.reduce((total, fii) => {
    return total + (fii.ultimo_provento * (fii.quantidade || 0))
  }, 0)
})

// Dados do gráfico
const chartOptions = computed(() => {
  const dados = fiis.value.reduce((acc, fii) => {
    const valor = fii.preco_atual * (fii.quantidade || 0)
    acc[fii.segmento] = (acc[fii.segmento] || 0) + valor
    return acc
  }, {})

  const series = [{
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: true,
    itemStyle: {
      borderRadius: 10,
      borderColor: '#fff',
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}: {d}%'
    },
    emphasis: {
      label: {
        show: true,
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    data: Object.entries(dados).map(([name, value]) => ({ name, value }))
  }]

  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series
  }
})

// Headers da tabela
const headers = [
  { title: 'Código', key: 'codigo', align: 'start', sortable: true },
  { title: 'Nome', key: 'nome', align: 'start', sortable: true },
  { title: 'Segmento', key: 'segmento', align: 'start', sortable: true },
  { title: 'Preço Atual', key: 'preco_atual', align: 'end', sortable: true },
  { title: 'DY', key: 'dividend_yield', align: 'end', sortable: true },
  { title: 'Liquidez Diária', key: 'liquidez_diaria', align: 'end', sortable: true },
  { title: 'Ações', key: 'actions', align: 'center', sortable: false }
]

// Métodos
const carregarDados = async () => {
  await carregarFIIs()
  await carregarInsights()
}

const carregarInsights = async () => {
  loadingInsights.value = true
  try {
    // Simular carregamento de insights (substituir por chamada real)
    await new Promise(resolve => setTimeout(resolve, 1000))
    insights.value = [
      {
        title: 'Concentração de Segmento',
        subtitle: 'Alta exposição ao setor de Logística',
        icon: 'mdi-alert',
        color: 'warning'
      },
      {
        title: 'Oportunidade de Diversificação',
        subtitle: 'Considere FIIs de Shoppings',
        icon: 'mdi-trending-up',
        color: 'success'
      }
    ]
  } catch (error) {
    console.error('Erro ao carregar insights:', error)
  } finally {
    loadingInsights.value = false
  }
}

const editarFII = (fii) => {
  fiiSelecionado.value = fii
  showEditDialog.value = true
}

const confirmarRemocao = (fii) => {
  fiiSelecionado.value = fii
  showConfirmDialog.value = true
}

const removerFIISelecionado = async () => {
  if (!fiiSelecionado.value) return
  
  try {
    await removerFII(fiiSelecionado.value.id)
    showConfirmDialog.value = false
  } catch (error) {
    console.error('Erro ao remover FII:', error)
  }
}

const alternarFavorito = async (id) => {
  try {
    await toggleFavorito(id)
  } catch (error) {
    console.error('Erro ao alterar favorito:', error)
  }
}

const verAnaliseCompleta = () => {
  router.push('/fiis/analise')
}

// Formatadores
const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value || 0)
}

const formatPercentage = (value) => {
  return `${(value || 0).toFixed(2)}%`
}

const getDYColor = (dy) => {
  if (dy >= 8) return 'success'
  if (dy >= 6) return 'info'
  if (dy >= 4) return 'warning'
  return 'error'
}

// Lifecycle
onMounted(() => {
  carregarDados()
})
</script>

<style lang="scss" scoped>
.fii-dashboard {
  .v-data-table {
    .v-data-table-header {
      background-color: rgb(var(--v-theme-surface));
    }
  }
}

:deep(.echarts) {
  min-height: 300px;
}
</style> 