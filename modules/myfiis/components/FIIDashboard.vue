<template>
  <div class="fii-dashboard">
    <VContainer>
      <VRow>
        <VCol cols="12">
          <page-header title="Meus FIIs">
            <template v-slot:actions>
              <add-fii-dialog />
            </template>
          </page-header>
        </VCol>
      </VRow>

      <VRow>
        <VCol cols="12" md="4">
          <metric-card
            title="Total Investido"
            :value="formatCurrency(totalInvestido)"
            icon="mdi-cash"
            color="primary"
          />
        </VCol>
        <VCol cols="12" md="4">
          <metric-card
            title="Rendimento Mensal"
            :value="formatCurrency(rendimentoMensal)"
            icon="mdi-chart-line"
            color="success"
          />
        </VCol>
        <VCol cols="12" md="4">
          <metric-card
            title="Dividend Yield Médio"
            :value="formatPercentage(dyMedio)"
            icon="mdi-percent"
            color="info"
          />
        </VCol>
      </VRow>

      <VRow>
        <VCol cols="12">
          <VCard>
            <VCardTitle class="d-flex align-center">
              <span>Lista de FIIs</span>
              <VSpacer></VSpacer>
              <VTextField
                v-model="search"
                append-icon="mdi-magnify"
                label="Buscar"
                single-line
                hide-details
                density="compact"
                class="ml-4"
                style="max-width: 300px"
              ></VTextField>
            </VCardTitle>

            <VDataTable
              :headers="headers"
              :items="fiis"
              :search="search"
              :loading="loading"
              density="comfortable"
            >
              <template v-slot:item.preco_atual="{ item }">
                {{ formatCurrency(item.raw.preco_atual) }}
              </template>

              <template v-slot:item.dividend_yield="{ item }">
                {{ formatPercentage(item.raw.dividend_yield) }}
              </template>

              <template v-slot:item.patrimonio_liquido="{ item }">
                {{ formatCurrency(item.raw.patrimonio_liquido) }}
              </template>

              <template v-slot:item.valor_patrimonial="{ item }">
                {{ formatCurrency(item.raw.valor_patrimonial) }}
              </template>

              <template v-slot:item.liquidez_diaria="{ item }">
                {{ formatCurrency(item.raw.liquidez_diaria) }}
              </template>

              <template v-slot:item.actions="{ item }">
                <VBtn
                  icon="mdi-pencil"
                  size="small"
                  variant="text"
                  @click="handleEdit(item.raw)"
                ></VBtn>
                <VBtn
                  icon="mdi-delete"
                  size="small"
                  variant="text"
                  color="error"
                  @click="handleDelete(item.raw)"
                ></VBtn>
              </template>
            </VDataTable>
          </VCard>
        </VCol>
      </VRow>
    </VContainer>

    <confirm-dialog
      v-model="showDeleteDialog"
      title="Excluir FII"
      text="Tem certeza que deseja excluir este FII?"
      @confirm="confirmDelete"
    />

    <edit-fii-dialog
      v-if="selectedFII"
      v-model="showEditDialog"
      :fii="selectedFII"
    />
  </div>
</template>

<script setup>
import MetricCard from '@/components/base/MetricCard.vue'
import PageHeader from '@/components/base/PageHeader.vue'
import ConfirmDialog from '@/components/modals/ConfirmDialog.vue'
import { formatCurrency, formatPercentage } from '@/utils/format'
import { computed, onMounted, ref } from 'vue'
import { useMyFIIs } from '../composables/useMyFIIs'

const search = ref('')
const showDeleteDialog = ref(false)
const selectedFII = ref(null)
const showEditDialog = ref(false)

const { fiis, loading, fetchMyFIIs, deleteFII } = useMyFIIs()

const headers = [
  { title: 'Código', key: 'codigo', align: 'start', sortable: true },
  { title: 'Nome', key: 'nome', align: 'start', sortable: true },
  { title: 'Segmento', key: 'segmento', align: 'start', sortable: true },
  { title: 'Preço Atual', key: 'preco_atual', align: 'end', sortable: true },
  { title: 'DY (%)', key: 'dividend_yield', align: 'end', sortable: true },
  { title: 'Patrimônio Líquido', key: 'patrimonio_liquido', align: 'end', sortable: true },
  { title: 'Valor Patrimonial', key: 'valor_patrimonial', align: 'end', sortable: true },
  { title: 'Liquidez Diária', key: 'liquidez_diaria', align: 'end', sortable: true },
  { title: 'Ações', key: 'actions', align: 'center', sortable: false }
]

const totalInvestido = computed(() => {
  return fiis.value.reduce((total, fii) => total + fii.preco_atual, 0)
})

const rendimentoMensal = computed(() => {
  return fiis.value.reduce((total, fii) => {
    return total + (fii.preco_atual * (fii.dividend_yield / 100) / 12)
  }, 0)
})

const dyMedio = computed(() => {
  if (fiis.value.length === 0) return 0
  return fiis.value.reduce((total, fii) => total + fii.dividend_yield, 0) / fiis.value.length
})

const handleEdit = (fii) => {
  selectedFII.value = fii
  showEditDialog.value = true
}

const handleDelete = (fii) => {
  selectedFII.value = fii
  showDeleteDialog.value = true
}

const confirmDelete = async () => {
  if (selectedFII.value) {
    await deleteFII(selectedFII.value.id)
    showDeleteDialog.value = false
    selectedFII.value = null
  }
}

onMounted(() => {
  fetchMyFIIs()
})
</script>

<style scoped>
.fii-dashboard {
  padding: 16px;
}

.v-card-title {
  padding: 16px;
}
</style> 