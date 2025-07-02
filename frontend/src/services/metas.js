import { api } from '@/boot/axios'

export const metasService = {
  // Listar todas as metas
  async listarMetas(filtros = {}) {
    try {
      const params = new URLSearchParams()
      
      if (filtros.status) {
        params.append('status', filtros.status)
      }
      if (filtros.skip) {
        params.append('skip', filtros.skip)
      }
      if (filtros.limit) {
        params.append('limit', filtros.limit)
      }
      
      const url = params.toString() ? `/metas?${params.toString()}` : '/metas'
      const response = await api.get(url)
      return response.data
    } catch (error) {
      console.error('Erro ao listar metas:', error)
      throw error
    }
  },

  // Obter meta por ID
  async obterMeta(metaId) {
    try {
      const response = await api.get(`/metas/${metaId}`)
      return response.data
    } catch (error) {
      console.error('Erro ao obter meta:', error)
      throw error
    }
  },

  // Criar nova meta
  async criarMeta(metaData) {
    try {
      const response = await api.post('/metas', metaData)
      return response.data
    } catch (error) {
      console.error('Erro ao criar meta:', error)
      throw error
    }
  },

  // Atualizar meta existente
  async atualizarMeta(metaId, metaData) {
    try {
      const response = await api.put(`/metas/${metaId}`, metaData)
      return response.data
    } catch (error) {
      console.error('Erro ao atualizar meta:', error)
      throw error
    }
  },

  // Deletar meta
  async deletarMeta(metaId) {
    try {
      const response = await api.delete(`/metas/${metaId}`)
      return response.data
    } catch (error) {
      console.error('Erro ao deletar meta:', error)
      throw error
    }
  },

  // Atualizar valor atual da meta
  async atualizarValorMeta(metaId, novoValor) {
    try {
      const response = await api.post(`/metas/${metaId}/atualizar-valor`, null, {
        params: { novo_valor: novoValor }
      })
      return response.data
    } catch (error) {
      console.error('Erro ao atualizar valor da meta:', error)
      throw error
    }
  },

  // Obter resumo estatístico
  async obterResumoEstatisticas() {
    try {
      const response = await api.get('/metas/resumo/estatisticas')
      return response.data
    } catch (error) {
      console.error('Erro ao obter resumo de metas:', error)
      throw error
    }
  },

  // Métodos auxiliares para filtros
  getStatusOptions() {
    return [
      { label: 'Todas', value: '' },
      { label: 'Ativas', value: 'ATIVA' },
      { label: 'Concluídas', value: 'CONCLUIDA' },
      { label: 'Pausadas', value: 'PAUSADA' },
      { label: 'Canceladas', value: 'CANCELADA' }
    ]
  },

  // Validações
  validarMeta(metaData) {
    const erros = []
    
    if (!metaData.titulo || metaData.titulo.trim() === '') {
      erros.push('Título é obrigatório')
    }
    
    if (!metaData.valor_meta || metaData.valor_meta <= 0) {
      erros.push('Valor da meta deve ser maior que zero')
    }
    
    if (!metaData.data_inicio) {
      erros.push('Data de início é obrigatória')
    }
    
    if (!metaData.data_fim) {
      erros.push('Data de fim é obrigatória')
    }
    
    if (metaData.data_inicio && metaData.data_fim) {
      const dataInicio = new Date(metaData.data_inicio)
      const dataFim = new Date(metaData.data_fim)
      
      if (dataFim <= dataInicio) {
        erros.push('Data de fim deve ser posterior à data de início')
      }
    }
    
    return erros
  },

  // Formatadores
  formatarStatus(status) {
    const statusMap = {
      'ATIVA': { label: 'Ativa', color: 'primary', icon: 'mdi-play' },
      'CONCLUIDA': { label: 'Concluída', color: 'success', icon: 'mdi-check-circle' },
      'PAUSADA': { label: 'Pausada', color: 'warning', icon: 'mdi-pause' },
      'CANCELADA': { label: 'Cancelada', color: 'error', icon: 'mdi-close-circle' }
    }
    
    return statusMap[status] || { label: status, color: 'grey', icon: 'mdi-help' }
  },

  calcularProgresso(valorAtual, valorMeta) {
    if (!valorMeta || valorMeta <= 0) return 0
    const progresso = (valorAtual / valorMeta) * 100
    return Math.min(progresso, 100) // Máximo 100%
  },

  calcularDiasRestantes(dataFim) {
    if (!dataFim) return 0
    const hoje = new Date()
    const fim = new Date(dataFim)
    const diffTime = fim - hoje
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return Math.max(diffDays, 0)
  },

  getCorProgresso(progresso) {
    if (progresso >= 100) return 'success'
    if (progresso >= 75) return 'primary'
    if (progresso >= 50) return 'warning'
    if (progresso >= 25) return 'orange'
    return 'error'
  }
} 