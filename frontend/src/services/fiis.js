import { api } from '@/boot/axios'

/**
 * Serviço para gerenciamento de FIIs
 */
export const FIIsService = {
  /**
   * Lista todos os FIIs
   */
  async listarFIIs() {
    const response = await api.get('/api/v1/myfiis/')
    return response.data
  },

  /**
   * Adiciona um novo FII
   */
  async criarFII(fiiData) {
    const response = await api.post('/api/v1/myfiis/', fiiData)
    return response.data
  },

  /**
   * Obtém detalhes de um FII específico
   */
  async obterFII(id) {
    const response = await api.get(`/api/v1/myfiis/${id}`)
    return response.data
  },

  /**
   * Atualiza um FII existente
   */
  async atualizarFII(id, fiiData) {
    const response = await api.put(`/api/v1/myfiis/${id}`, fiiData)
    return response.data
  },

  /**
   * Remove um FII
   */
  async removerFII(id) {
    const response = await api.delete(`/api/v1/myfiis/${id}`)
    return response.data
  },

  /**
   * Obtém resumo do dashboard de FIIs
   */
  async obterAnalytics() {
    const response = await api.get('/api/v1/myfiis/analytics/summary')
    return response.data
  },

  /**
   * Busca FIIs por termo
   */
  async buscarFIIs(termo) {
    const response = await api.get(`/api/v1/myfiis/search?q=${termo}`)
    return response.data
  },

  /**
   * Alterna favorito de um FII
   */
  async alternarFavorito(id) {
    const response = await api.patch(`/api/v1/myfiis/${id}/favorito`)
    return response.data
  },

  /**
   * Obtém insights de um FII específico
   */
  async obterInsights(id) {
    const response = await api.get(`/api/v1/myfiis/${id}/insights`)
    return response.data
  }
} 