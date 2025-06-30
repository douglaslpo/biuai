<template>
  <div class="analise-grafico">
    <q-chart
      type="line"
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'AnaliseGrafico',

  props: {
    dados: {
      type: Array,
      required: true,
      default: () => []
    }
  },

  setup (props) {
    const chartData = computed(() => ({
      labels: props.dados.map(d => d.mes),
      datasets: [
        {
          label: 'Receitas',
          data: props.dados.map(d => d.receitas),
          borderColor: '#21BA45',
          backgroundColor: 'rgba(33, 186, 69, 0.1)',
          fill: true
        },
        {
          label: 'Despesas',
          data: props.dados.map(d => d.despesas),
          borderColor: '#C10015',
          backgroundColor: 'rgba(193, 0, 21, 0.1)',
          fill: true
        }
      ]
    }))

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        },
        title: {
          display: true,
          text: 'Evolução Financeira'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => `R$ ${value.toLocaleString('pt-BR')}`
          }
        }
      }
    }

    return {
      chartData,
      chartOptions
    }
  }
})
</script>

<style lang="scss" scoped>
.analise-grafico {
  height: 400px;
  width: 100%;
}
</style> 