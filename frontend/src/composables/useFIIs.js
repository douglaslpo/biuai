import { FIIsService } from '@/services/fiis'
import { computed, ref } from 'vue'
import { useNotificacoes } from './useNotificacoes'

export function useFIIs() {
  const fiis = ref([])
  const loading = ref(false)
  const error = ref(null)
  const analytics = ref(null)
  const { notificar } = useNotificacoes()

  // Getters computados
  const totalInvestido = computed(() => analytics.value?.total_investido || 0)
  const rendimentoMensal = computed(() => analytics.value?.rendimento_mensal || 0)
  const dyMedio = computed(() => analytics.value?.dy_medio || 0)
  const totalFIIs = computed(() => analytics.value?.total_fiis || 0)

  const segmentos = computed(() => {
    const segs = fiis.value.reduce((acc, fii) => {
      acc[fii.segmento] = (acc[fii.segmento] || 0) + 1
      return acc
    }, {})
    return Object.entries(segs).map(([nome, quantidade]) => ({
      nome,
      quantidade
    }))
  })

  // Ações
  async function carregarFIIs() {
    loading.value = true
    error.value = null
    try {
      fiis.value = await FIIsService.listarFIIs()
      await carregarAnalytics()
    } catch (err) {
      error.value = 'Erro ao carregar FIIs'
      notificar({
        tipo: 'error',
        mensagem: 'Não foi possível carregar os FIIs'
      })
    } finally {
      loading.value = false
    }
  }

  async function carregarAnalytics() {
    try {
      analytics.value = await FIIsService.obterAnalytics()
    } catch (err) {
      notificar({
        tipo: 'error',
        mensagem: 'Erro ao carregar análises'
      })
    }
  }

  async function adicionarFII(fiiData) {
    loading.value = true
    error.value = null
    try {
      const novoFII = await FIIsService.criarFII(fiiData)
      fiis.value.push(novoFII)
      await carregarAnalytics()
      notificar({
        tipo: 'success',
        mensagem: 'FII adicionado com sucesso'
      })
      return novoFII
    } catch (err) {
      error.value = 'Erro ao adicionar FII'
      notificar({
        tipo: 'error',
        mensagem: 'Não foi possível adicionar o FII'
      })
      throw err
    } finally {
      loading.value = false
    }
  }

  async function atualizarFII(id, fiiData) {
    loading.value = true
    error.value = null
    try {
      const fiiAtualizado = await FIIsService.atualizarFII(id, fiiData)
      const index = fiis.value.findIndex(f => f.id === id)
      if (index !== -1) {
        fiis.value[index] = fiiAtualizado
      }
      await carregarAnalytics()
      notificar({
        tipo: 'success',
        mensagem: 'FII atualizado com sucesso'
      })
      return fiiAtualizado
    } catch (err) {
      error.value = 'Erro ao atualizar FII'
      notificar({
        tipo: 'error',
        mensagem: 'Não foi possível atualizar o FII'
      })
      throw err
    } finally {
      loading.value = false
    }
  }

  async function removerFII(id) {
    loading.value = true
    error.value = null
    try {
      await FIIsService.removerFII(id)
      fiis.value = fiis.value.filter(f => f.id !== id)
      await carregarAnalytics()
      notificar({
        tipo: 'success',
        mensagem: 'FII removido com sucesso'
      })
    } catch (err) {
      error.value = 'Erro ao remover FII'
      notificar({
        tipo: 'error',
        mensagem: 'Não foi possível remover o FII'
      })
      throw err
    } finally {
      loading.value = false
    }
  }

  async function obterInsights(id) {
    try {
      return await FIIsService.obterInsights(id)
    } catch (err) {
      notificar({
        tipo: 'error',
        mensagem: 'Erro ao obter insights do FII'
      })
      throw err
    }
  }

  return {
    // Estado
    fiis,
    loading,
    error,
    analytics,

    // Getters
    totalInvestido,
    rendimentoMensal,
    dyMedio,
    totalFIIs,
    segmentos,

    // Ações
    carregarFIIs,
    adicionarFII,
    atualizarFII,
    removerFII,
    obterInsights
  }
} 