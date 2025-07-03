<template>
  <v-card 
    class="meta-card" 
    elevation="4" 
    hover 
    @click="$emit('view', meta)"
  >
    <v-card-title class="pa-4 pb-2">
      <div class="d-flex align-center justify-space-between w-100">
        <span class="text-h6 font-weight-bold">{{ meta.titulo || meta.descricao || 'Meta' }}</span>
        <v-chip
          :color="getStatusColor(meta.status)"
          :prepend-icon="getStatusIcon(meta.status)"
          size="small"
          variant="elevated"
        >
          {{ getStatusLabel(meta.status) }}
        </v-chip>
      </div>
    </v-card-title>

    <v-card-text class="pa-4">
      <div class="meta-info mb-4">
        <div v-if="meta.descricao" class="meta-description text-body-2 mb-3">
          {{ truncateText(meta.descricao, 80) }}
        </div>
        
        <div class="meta-valores mb-3">
          <div class="d-flex justify-space-between mb-2">
            <span class="text-body-2">Progresso:</span>
            <span class="text-body-2 font-weight-bold">
              {{ formatCurrency(meta.valor_atual || 0) }} / {{ formatCurrency(meta.valor_meta || 0) }}
            </span>
          </div>
          
          <v-progress-linear
            :model-value="progressoPercentual"
            :color="getProgressColor(progressoPercentual)"
            height="8"
            rounded
            class="mb-2"
          />
          
          <div class="d-flex justify-space-between">
            <span class="text-body-2">{{ progressoPercentual }}% concluído</span>
            <span class="text-body-2">
              {{ diasRestantes > 0 ? `${diasRestantes} dias restantes` : 'Vencida' }}
            </span>
          </div>
        </div>

        <div v-if="meta.categoria" class="meta-categoria">
          <v-chip size="small" color="secondary" variant="tonal">
            {{ meta.categoria }}
          </v-chip>
        </div>

        <!-- Data de vencimento -->
        <div v-if="meta.data_fim" class="meta-prazo mt-2">
          <v-chip 
            size="small" 
            :color="getDueDateColor()" 
            variant="tonal"
            prepend-icon="mdi-calendar"
          >
            {{ formatDate(meta.data_fim) }}
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
        @click.stop="$emit('addProgress', meta)"
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
          <v-list-item @click="$emit('edit', meta)">
            <v-list-item-title>
              <v-icon icon="mdi-pencil" class="mr-2" />
              Editar
            </v-list-item-title>
          </v-list-item>
          
          <v-list-item @click="$emit('view', meta)">
            <v-list-item-title>
              <v-icon icon="mdi-eye" class="mr-2" />
              Ver Detalhes
            </v-list-item-title>
          </v-list-item>
          
          <v-list-item @click="$emit('delete', meta)">
            <v-list-item-title class="text-error">
              <v-icon icon="mdi-delete" class="mr-2" />
              Excluir
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  meta: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['edit', 'delete', 'view', 'addProgress'])

// Computed
const progressoPercentual = computed(() => {
  if (!props.meta.valor_meta || props.meta.valor_meta === 0) return 0
  const progresso = (props.meta.valor_atual || 0) / props.meta.valor_meta * 100
  return Math.min(Math.round(progresso), 100)
})

const diasRestantes = computed(() => {
  if (!props.meta.data_fim) return 0
  const hoje = new Date()
  const dataFim = new Date(props.meta.data_fim)
  const diffTime = dataFim - hoje
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
})

// Methods
const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value || 0)
}

const formatDate = (date) => {
  if (!date) return ''
  return new Intl.DateTimeFormat('pt-BR').format(new Date(date))
}

const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const getStatusColor = (status) => {
  const colors = {
    ativa: 'info',
    concluida: 'success',
    pausada: 'warning',
    vencida: 'error'
  }
  return colors[status] || 'primary'
}

const getStatusIcon = (status) => {
  const icons = {
    ativa: 'mdi-play',
    concluida: 'mdi-check-circle',
    pausada: 'mdi-pause',
    vencida: 'mdi-alert-circle'
  }
  return icons[status] || 'mdi-target'
}

const getStatusLabel = (status) => {
  const labels = {
    ativa: 'Ativa',
    concluida: 'Concluída',
    pausada: 'Pausada',
    vencida: 'Vencida'
  }
  return labels[status] || status
}

const getProgressColor = (progresso) => {
  if (progresso >= 100) return 'success'
  if (progresso >= 75) return 'info'
  if (progresso >= 50) return 'warning'
  if (progresso >= 25) return 'orange'
  return 'error'
}

const getDueDateColor = () => {
  if (diasRestantes.value <= 0) return 'error'
  if (diasRestantes.value <= 7) return 'warning'
  if (diasRestantes.value <= 30) return 'info'
  return 'success'
}
</script>

<style scoped>
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
  color: rgba(var(--v-theme-on-surface), 0.7);
  line-height: 1.4;
}

.meta-valores {
  background: rgba(var(--v-theme-surface), 0.5);
  border-radius: 8px;
  padding: 12px;
}

.meta-categoria {
  margin-top: 8px;
}

.meta-prazo {
  border-top: 1px solid rgba(var(--v-theme-surface), 0.12);
  padding-top: 8px;
}
</style> 