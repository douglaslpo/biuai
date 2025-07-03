<template>
  <v-card 
    class="conta-card" 
    elevation="4" 
    hover 
    @click="$emit('view', conta)"
    :class="{ 'conta-inativa': !conta.ativa }"
  >
    <v-card-title class="pa-4 pb-2">
      <div class="d-flex align-center justify-space-between w-100">
        <div class="d-flex align-center">
          <v-icon 
            :icon="getContaIcon(conta.tipo_conta)" 
            :color="getContaColor(conta.tipo_conta)"
            class="mr-2"
          />
          <span class="text-h6 font-weight-bold">{{ conta.nm_conta || 'Conta' }}</span>
        </div>
        <v-chip
          :color="conta.ativa ? 'success' : 'error'"
          :prepend-icon="conta.ativa ? 'mdi-check' : 'mdi-pause'"
          size="small"
          variant="elevated"
        >
          {{ conta.ativa ? 'Ativa' : 'Inativa' }}
        </v-chip>
      </div>
    </v-card-title>

    <v-card-text class="pa-4">
      <div class="conta-info">
        <div class="conta-detalhes mb-3">
          <div class="text-body-2 mb-1">
            <strong>Banco:</strong> {{ conta.banco?.nm_banco || 'N/A' }}
          </div>
          <div v-if="conta.numero_conta" class="text-body-2 mb-1">
            <strong>Conta:</strong> {{ formatarNumeroConta(conta.numero_conta, conta.agencia) }}
          </div>
          <div v-if="conta.tipo_conta" class="text-body-2 mb-1">
            <strong>Tipo:</strong> {{ getContaLabel(conta.tipo_conta) }}
          </div>
        </div>

        <div class="saldo-info">
          <v-card 
            class="saldo-card pa-3" 
            :color="getSaldoColor(conta.saldo_atual)"
            variant="tonal"
          >
            <div class="text-center">
              <div class="text-body-2 mb-1">Saldo Atual</div>
              <div class="text-h6 font-weight-bold">
                {{ formatCurrency(conta.saldo_atual) }}
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
                {{ formatCurrency(conta.total_receitas) }}
              </div>
            </v-col>
            <v-col cols="4" class="text-center">
              <div class="text-caption text-error">Despesas</div>
              <div class="text-body-2 font-weight-bold text-error">
                {{ formatCurrency(conta.total_despesas) }}
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
        @click.stop="$emit('view', conta)"
      >
        Ver Detalhes
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
          <v-list-item @click="$emit('edit', conta)">
            <v-list-item-title>
              <v-icon icon="mdi-pencil" class="mr-2" />
              Editar
            </v-list-item-title>
          </v-list-item>
          
          <v-list-item @click="$emit('delete', conta)">
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
  conta: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['edit', 'delete', 'view'])

// Methods
const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value || 0)
}

const formatarNumeroConta = (numero, agencia) => {
  if (!numero) return 'N/A'
  return agencia ? `${agencia} / ${numero}` : numero
}

const getContaIcon = (tipo) => {
  const icons = {
    corrente: 'mdi-credit-card',
    poupanca: 'mdi-piggy-bank',
    investimento: 'mdi-chart-line'
  }
  return icons[tipo] || 'mdi-bank'
}

const getContaColor = (tipo) => {
  const colors = {
    corrente: 'primary',
    poupanca: 'success',
    investimento: 'warning'
  }
  return colors[tipo] || 'primary'
}

const getContaLabel = (tipo) => {
  const labels = {
    corrente: 'Conta Corrente',
    poupanca: 'Conta Poupança',
    investimento: 'Conta Investimento'
  }
  return labels[tipo] || tipo
}

const getSaldoColor = (saldo) => {
  const valor = Number(saldo) || 0
  if (valor > 0) return 'success'
  if (valor < 0) return 'error'
  return 'info'
}
</script>

<style scoped>
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
  background: rgba(var(--v-theme-surface), 0.5);
  border-radius: 8px;
  padding: 8px;
}
</style> 