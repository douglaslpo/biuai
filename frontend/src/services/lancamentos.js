import { api } from '@/boot/axios'

export const LancamentosService = {
  async listar(params = {}) {
    const response = await api.get('/financeiro', { params })
    return response.data
  },

  async criar(lancamento) {
    const response = await api.post('/financeiro', lancamento)
    return response.data
  },

  async atualizar(id, lancamento) {
    const response = await api.put(`/financeiro/${id}`, lancamento)
    return response.data
  },

  async excluir(id) {
    const response = await api.delete(`/financeiro/${id}`)
    return response.data
  },

  async obterPorId(id) {
    const response = await api.get(`/financeiro/${id}`)
    return response.data
  },

  async obterSummary(periodoDias = 30) {
    const response = await api.get('/financeiro/summary/stats', {
      params: { periodo_dias: periodoDias }
    })
    return response.data
  },

  async buscar(query) {
    const response = await api.get('/financeiro', {
      params: { search: query }
    })
    return response.data
  },

  async filtrarPorData(dataInicio, dataFim) {
    const response = await api.get('/financeiro', {
      params: {
        data_inicio: dataInicio,
        data_fim: dataFim
      }
    })
    return response.data
  }
} 