<template>
  <v-card class="intelligent-insights-card" elevation="8">
    <v-card-title class="d-flex align-center pa-4">
      <v-icon icon="mdi-brain" color="primary" class="me-3" size="large" />
      <div class="flex-grow-1">
        <h3 class="text-h6 font-weight-bold">🧠 Insights Inteligentes</h3>
        <p class="text-caption text-medium-emphasis ma-0">Análise IA dos seus dados financeiros</p>
      </div>
      <v-btn
        icon="mdi-refresh"
        variant="text"
        size="small"
        :loading="loading"
        @click="refreshInsights"
      />
    </v-card-title>

    <v-divider />

    <v-card-text class="pa-0">
      <!-- Loading State -->
      <div v-if="loading" class="d-flex justify-center align-center py-8">
        <div class="text-center">
          <v-progress-circular
            indeterminate
            color="primary"
            size="48"
            class="mb-4"
          />
          <p class="text-body-2 text-medium-emphasis">Analisando seus dados...</p>
        </div>
      </div>

      <!-- Insights List -->
      <div v-else-if="insights.length > 0" class="insights-container">
        <v-list lines="two" class="pa-0">
          <template v-for="(insight, index) in insights" :key="insight.id">
            <v-list-item
              class="insight-item"
              :class="[
                `insight-${insight.type}`,
                { 'insight-expanded': expandedInsight === insight.id }
              ]"
              @click="toggleInsight(insight)"
            >
              <template #prepend>
                <v-avatar
                  :color="getInsightColor(insight)"
                  variant="tonal"
                  size="48"
                  class="me-3"
                >
                  <v-icon :icon="insight.icon" />
                </v-avatar>
              </template>

              <v-list-item-title class="font-weight-medium">
                {{ insight.title }}
              </v-list-item-title>
              
              <v-list-item-subtitle class="text-wrap">
                {{ insight.description }}
              </v-list-item-subtitle>

              <template #append>
                <div class="d-flex flex-column align-center">
                  <v-chip
                    :color="getPriorityColor(insight.priority)"
                    variant="tonal"
                    size="small"
                    class="mb-2"
                  >
                    {{ getPriorityLabel(insight.priority) }}
                  </v-chip>
                  
                  <v-btn
                    :icon="expandedInsight === insight.id ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                    variant="text"
                    size="small"
                    @click.stop="toggleInsight(insight)"
                  />
                </div>
              </template>
            </v-list-item>

            <!-- Expanded Content -->
            <v-expand-transition>
              <div v-if="expandedInsight === insight.id" class="expanded-content">
                <v-card
                  variant="tonal"
                  :color="getInsightColor(insight)"
                  class="mx-4 mb-4"
                >
                  <v-card-text>
                    <!-- AI Generated Details -->
                    <div v-if="insightDetails[insight.id]" class="mb-4">
                      <h4 class="text-subtitle-1 mb-2">
                        <v-icon icon="mdi-robot" class="me-2" />
                        Análise Detalhada da IA
                      </h4>
                      <p class="text-body-2">{{ insightDetails[insight.id].analysis }}</p>
                      
                      <!-- Recommendations -->
                      <div v-if="insightDetails[insight.id].recommendations" class="mt-3">
                        <h5 class="text-subtitle-2 mb-2">💡 Recomendações:</h5>
                        <v-chip-group>
                          <v-chip
                            v-for="rec in insightDetails[insight.id].recommendations"
                            :key="rec"
                            variant="outlined"
                            size="small"
                            @click="executeRecommendation(rec, insight)"
                          >
                            {{ rec }}
                          </v-chip>
                        </v-chip-group>
                      </div>
                    </div>

                    <!-- Loading AI Analysis -->
                    <div v-else class="text-center py-4">
                      <v-progress-circular indeterminate size="24" />
                      <p class="text-caption mt-2">Gerando análise IA...</p>
                    </div>

                    <!-- Action Buttons -->
                    <div v-if="insight.actionable" class="d-flex gap-2 mt-4">
                      <v-btn
                        color="primary"
                        variant="elevated"
                        size="small"
                        prepend-icon="mdi-chart-line"
                        @click="openAnalytics(insight)"
                      >
                        Ver Análise
                      </v-btn>
                      
                      <v-btn
                        color="success"
                        variant="outlined"
                        size="small"
                        prepend-icon="mdi-lightbulb"
                        @click="getSuggestions(insight)"
                      >
                        Sugestões IA
                      </v-btn>
                    </div>
                  </v-card-text>
                </v-card>
              </div>
            </v-expand-transition>

            <v-divider v-if="index < insights.length - 1" />
          </template>
        </v-list>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state pa-6 text-center">
        <v-icon icon="mdi-lightbulb-outline" size="64" color="grey" class="mb-4" />
        <h4 class="text-h6 mb-2">Sem insights disponíveis</h4>
        <p class="text-body-2 text-medium-emphasis mb-4">
          Adicione mais transações para receber insights personalizados
        </p>
        <v-btn color="primary" variant="elevated" @click="$emit('add-transaction')">
          Adicionar Lançamento
        </v-btn>
      </div>
    </v-card-text>

    <!-- AI Suggestions Dialog -->
    <v-dialog v-model="showSuggestionsDialog" max-width="600">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-robot" class="me-2" />
          Sugestões Inteligentes da IA
        </v-card-title>
        
        <v-card-text>
          <div v-if="loadingSuggestions" class="text-center py-4">
            <v-progress-circular indeterminate />
            <p class="mt-2">Gerando sugestões personalizadas...</p>
          </div>
          
          <div v-else-if="aiSuggestions.length > 0">
            <v-list>
              <v-list-item
                v-for="suggestion in aiSuggestions"
                :key="suggestion.id"
                @click="applySuggestion(suggestion)"
              >
                <template #prepend>
                  <v-icon :icon="suggestion.icon" :color="suggestion.color" />
                </template>
                <v-list-item-title>{{ suggestion.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ suggestion.description }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="showSuggestionsDialog = false">Fechar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// Props
const props = defineProps({
  insights: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['refresh', 'add-transaction'])

// Router
const router = useRouter()

// State
const expandedInsight = ref(null)
const insightDetails = ref({})
const showSuggestionsDialog = ref(false)
const loadingSuggestions = ref(false)
const aiSuggestions = ref([])

// Methods
const toggleInsight = async (insight) => {
  if (expandedInsight.value === insight.id) {
    expandedInsight.value = null
  } else {
    expandedInsight.value = insight.id
    
    if (!insightDetails.value[insight.id]) {
      await loadInsightDetails(insight)
    }
  }
}

const loadInsightDetails = async (insight) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const details = generateAIAnalysis(insight)
    insightDetails.value[insight.id] = details
  } catch (error) {
    console.error('Erro ao carregar detalhes do insight:', error)
  }
}

const generateAIAnalysis = (insight) => {
  const analyses = {
    'savings_rate': {
      analysis: 'Baseado na análise dos seus padrões de gasto, sua taxa de economia está dentro da faixa recomendada. A IA identificou que você tem disciplina financeira consistente.',
      recommendations: ['Automatizar Investimentos', 'Revisar Gastos Variáveis', 'Aumentar Reserva']
    },
    'top_category': {
      analysis: 'A concentração de gastos nesta categoria indica um padrão comportamental. A IA sugere estratégias de otimização baseadas em usuários similares.',
      recommendations: ['Definir Orçamento', 'Buscar Alternativas', 'Planejar Compras']
    },
    'default': {
      analysis: 'A análise preditiva da IA identifica oportunidades de melhoria na sua gestão financeira.',
      recommendations: ['Diversificar Investimentos', 'Otimizar Tributação', 'Aumentar Renda']
    }
  }
  
  return analyses[insight.id] || analyses.default
}

const refreshInsights = () => {
  emit('refresh')
}

const openAnalytics = (insight) => {
  router.push('/analytics')
}

const getSuggestions = async (insight) => {
  showSuggestionsDialog.value = true
  loadingSuggestions.value = true
  
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    aiSuggestions.value = [
      {
        id: 1,
        title: 'Automatizar Economia',
        description: 'Configure transferências automáticas para poupança',
        icon: 'mdi-robot',
        color: 'primary'
      },
      {
        id: 2,
        title: 'Otimizar Categorias',
        description: 'Reorganize gastos para melhor controle',
        icon: 'mdi-tune',
        color: 'success'
      }
    ]
  } catch (error) {
    console.error('Erro ao gerar sugestões:', error)
  } finally {
    loadingSuggestions.value = false
  }
}

const applySuggestion = (suggestion) => {
  console.log('Aplicando sugestão:', suggestion)
  showSuggestionsDialog.value = false
}

const executeRecommendation = (recommendation, insight) => {
  console.log('Executando recomendação:', recommendation, insight)
}

// Utility functions
const getInsightColor = (insight) => {
  const colors = {
    'success': 'success',
    'warning': 'warning',
    'error': 'error',
    'info': 'info'
  }
  return colors[insight.type] || 'primary'
}

const getPriorityColor = (priority) => {
  const colors = {
    'high': 'error',
    'critical': 'error',
    'medium': 'warning',
    'low': 'success'
  }
  return colors[priority] || 'primary'
}

const getPriorityLabel = (priority) => {
  const labels = {
    'high': 'Alta',
    'critical': 'Crítica',
    'medium': 'Média',
    'low': 'Baixa'
  }
  return labels[priority] || 'Normal'
}
</script>

<style lang="scss" scoped>
.intelligent-insights-card {
  border-radius: 16px;
  overflow: hidden;
}

.insights-container {
  max-height: 400px;
  overflow-y: auto;
}

.insight-item {
  transition: all 0.3s ease;
  cursor: pointer;
  
  &:hover {
    background-color: rgba(var(--v-theme-primary), 0.04);
  }
  
  &.insight-expanded {
    background-color: rgba(var(--v-theme-primary), 0.08);
  }
}

.expanded-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.empty-state {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style> 