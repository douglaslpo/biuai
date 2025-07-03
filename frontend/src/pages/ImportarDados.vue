<template>
  <div class="importar-dados-page">
    <!-- Header da Página -->
    <div class="page-header mb-6">
      <h1 class="text-h4 mb-2">
        <v-icon icon="mdi-brain" class="mr-2" />
        Importação Inteligente de Dados
      </h1>
      <p class="text-subtitle-1 text-medium-emphasis">
        Análise automática de arquivos e geração de dados sintéticos com IA
      </p>
    </div>

    <v-row>
      <!-- Análise de Arquivo -->
      <v-col cols="12" md="8">
        <v-card elevation="2" class="mb-4">
          <v-card-title>
            <v-icon icon="mdi-file-search" class="mr-2" />
            Análise Automática de Arquivo
          </v-card-title>
          
          <v-card-text>
            <v-file-input
              v-model="selectedFile"
              accept=".csv,.xlsx,.xls"
              label="Selecione arquivo (CSV, Excel)"
              variant="outlined"
              density="comfortable"
              prepend-icon="mdi-paperclip"
              show-size
              clearable
              @update:model-value="onFileSelected"
            />

            <div class="mt-4 d-flex ga-3">
              <v-btn
                @click="analyzeFile"
                :disabled="!selectedFile"
                :loading="analyzingFile"
                color="primary"
                variant="elevated"
                prepend-icon="mdi-magnify"
              >
                Analisar Arquivo
              </v-btn>
              
              <v-btn
                v-if="analysisResult"
                @click="importFile"
                :loading="importingFile"
                color="success"
                variant="elevated"
                prepend-icon="mdi-database-import"
              >
                Importar Dados
              </v-btn>
            </div>

            <!-- Resultado da Análise -->
            <v-card v-if="analysisResult" class="mt-4" variant="tonal" color="info">
              <v-card-title class="text-h6">
                <v-icon icon="mdi-chart-line" class="mr-2" />
                Resultado da Análise
              </v-card-title>
              <v-card-text>
                <v-row>
                  <v-col cols="12" sm="6">
                    <v-list density="compact">
                      <v-list-item>
                        <template #prepend>
                          <v-icon icon="mdi-file-chart" />
                        </template>
                        <v-list-item-title>Tipo detectado:</v-list-item-title>
                        <v-list-item-subtitle>{{ analysisResult.detected_type }}</v-list-item-subtitle>
                      </v-list-item>
                      <v-list-item>
                        <template #prepend>
                          <v-icon icon="mdi-table" />
                        </template>
                        <v-list-item-title>Registros:</v-list-item-title>
                        <v-list-item-subtitle>{{ analysisResult.statistics.total_rows }}</v-list-item-subtitle>
                      </v-list-item>
                      <v-list-item>
                        <template #prepend>
                          <v-icon icon="mdi-view-column" />
                        </template>
                        <v-list-item-title>Colunas:</v-list-item-title>
                        <v-list-item-subtitle>{{ analysisResult.statistics.total_columns }}</v-list-item-subtitle>
                      </v-list-item>
                    </v-list>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-progress-linear
                      :model-value="analysisResult.mapping_confidence"
                      color="success"
                      height="20"
                      rounded
                    >
                      <template #default="{ value }">
                        <strong>{{ Math.ceil(value) }}% confiança</strong>
                      </template>
                    </v-progress-linear>
                    <p class="text-caption mt-2 text-center">
                      Confiança do mapeamento automático
                    </p>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Dados Sintéticos -->
      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title>
            <v-icon icon="mdi-creation" class="mr-2" />
            Dados Sintéticos
          </v-card-title>
          
          <v-card-text>
            <v-select
              v-model="syntheticType"
              :items="syntheticTypes"
              label="Tipo de dados"
              variant="outlined"
              density="comfortable"
              class="mb-4"
            />

            <v-text-field
              v-model.number="syntheticCount"
              type="number"
              label="Quantidade"
              variant="outlined"
              density="comfortable"
              min="10"
              max="10000"
              class="mb-4"
            />

            <v-btn
              @click="generateSynthetic"
              :loading="generatingData"
              color="secondary"
              variant="elevated"
              block
              prepend-icon="mdi-auto-fix"
            >
              Gerar Dados
            </v-btn>

            <v-btn
              v-if="syntheticResult"
              @click="importSynthetic"
              :loading="importingSynthetic"
              color="success"
              variant="elevated"
              block
              class="mt-2"
              prepend-icon="mdi-database-plus"
            >
              Importar Sintéticos
            </v-btn>

            <!-- Info sobre dados sintéticos -->
            <v-alert
              v-if="syntheticResult"
              type="success"
              variant="tonal"
              class="mt-4"
            >
              {{ syntheticResult.records_generated }} registros gerados com sucesso!
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Preview dos Dados -->
    <v-card v-if="previewData.length > 0" class="mt-6" elevation="2">
      <v-card-title>
        <v-icon icon="mdi-table-eye" class="mr-2" />
        Preview dos Dados
      </v-card-title>
      
      <v-card-text>
        <v-data-table
          :headers="previewHeaders"
          :items="previewData"
          density="compact"
          :items-per-page="5"
          class="elevation-0"
        />
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'ImportarDados',
  setup() {
    const selectedFile = ref(null)
    const syntheticCount = ref(100)
    const syntheticType = ref('financeiro')
    const analyzingFile = ref(false)
    const importingFile = ref(false)
    const generatingData = ref(false)
    const importingSynthetic = ref(false)
    
    const analysisResult = ref(null)
    const syntheticResult = ref(null)
    const previewData = ref([])
    const previewHeaders = ref([])

    const syntheticTypes = [
      { title: 'Financeiro Genérico', value: 'financeiro' },
      { title: 'SIOG Governamental', value: 'siog' },
      { title: 'Genérico', value: 'generic' }
    ]

    const onFileSelected = () => {
      analysisResult.value = null
      previewData.value = []
      previewHeaders.value = []
    }

    const analyzeFile = async () => {
      if (!selectedFile.value) return
      
      analyzingFile.value = true
      try {
        // Simular análise
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        analysisResult.value = {
          detected_type: 'financeiro',
          statistics: {
            total_rows: 1500,
            total_columns: 8
          },
          mapping_confidence: 87
        }

        // Simular preview
        previewHeaders.value = [
          { title: 'Descrição', key: 'descricao' },
          { title: 'Valor', key: 'valor' },
          { title: 'Data', key: 'data' },
          { title: 'Categoria', key: 'categoria' }
        ]
        
        previewData.value = [
          { descricao: 'Supermercado', valor: 'R$ 150,00', data: '2025-07-01', categoria: 'Alimentação' },
          { descricao: 'Combustível', valor: 'R$ 80,00', data: '2025-07-02', categoria: 'Transporte' }
        ]
      } catch (error) {
        console.error('Erro ao analisar arquivo:', error)
      } finally {
        analyzingFile.value = false
      }
    }

    const importFile = async () => {
      importingFile.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 1500))
        resetPage()
      } catch (error) {
        console.error('Erro ao importar arquivo:', error)
      } finally {
        importingFile.value = false
      }
    }

    const generateSynthetic = async () => {
      generatingData.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        syntheticResult.value = {
          records_generated: syntheticCount.value,
          type: syntheticType.value
        }
      } catch (error) {
        console.error('Erro ao gerar dados sintéticos:', error)
      } finally {
        generatingData.value = false
      }
    }

    const importSynthetic = async () => {
      importingSynthetic.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        syntheticResult.value = null
      } catch (error) {
        console.error('Erro ao importar dados sintéticos:', error)
      } finally {
        importingSynthetic.value = false
      }
    }

    const resetPage = () => {
      selectedFile.value = null
      analysisResult.value = null
      syntheticResult.value = null
      previewData.value = []
      previewHeaders.value = []
    }

    return {
      selectedFile,
      syntheticCount,
      syntheticType,
      syntheticTypes,
      analyzingFile,
      importingFile,
      generatingData,
      importingSynthetic,
      analysisResult,
      syntheticResult,
      previewData,
      previewHeaders,
      onFileSelected,
      analyzeFile,
      importFile,
      generateSynthetic,
      importSynthetic,
      resetPage
    }
  }
}
</script>

<style scoped>
.importar-dados-page {
  padding: 24px;
}

.page-header {
  text-align: center;
}
</style>
