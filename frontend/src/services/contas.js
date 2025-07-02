import { api } from '@/boot/axios'

export const contasService = {
  // Listar todas as contas
  async listarContas(filtros = {}) {
    try {
      const params = new URLSearchParams()
      
      if (filtros.ativa !== undefined) {
        params.append('ativa', filtros.ativa)
      }
      if (filtros.tipo_conta) {
        params.append('tipo_conta', filtros.tipo_conta)
      }
      if (filtros.skip) {
        params.append('skip', filtros.skip)
      }
      if (filtros.limit) {
        params.append('limit', filtros.limit)
      }
      
      const url = params.toString() ? `/contas?${params.toString()}` : '/contas'
      const response = await api.get(url)
      return response.data
    } catch (error) {
      console.error('Erro ao listar contas:', error)
      throw error
    }
  },

  // Obter conta por ID
  async obterConta(contaId) {
    try {
      const response = await api.get(`/contas/${contaId}`)
      return response.data
    } catch (error) {
      console.error('Erro ao obter conta:', error)
      throw error
    }
  },

  // Criar nova conta
  async criarConta(contaData) {
    try {
      const response = await api.post('/contas', contaData)
      return response.data
    } catch (error) {
      console.error('Erro ao criar conta:', error)
      throw error
    }
  },

  // Atualizar conta existente
  async atualizarConta(contaId, contaData) {
    try {
      const response = await api.put(`/contas/${contaId}`, contaData)
      return response.data
    } catch (error) {
      console.error('Erro ao atualizar conta:', error)
      throw error
    }
  },

  // Deletar conta
  async deletarConta(contaId) {
    try {
      const response = await api.delete(`/contas/${contaId}`)
      return response.data
    } catch (error) {
      console.error('Erro ao deletar conta:', error)
      throw error
    }
  },

  // Ativar ou desativar conta
  async alterarStatusConta(contaId, ativar = true) {
    try {
      const response = await api.patch(`/contas/${contaId}/ativar`, null, {
        params: { ativar }
      })
      return response.data
    } catch (error) {
      console.error('Erro ao alterar status da conta:', error)
      throw error
    }
  },

  // Obter resumo estatístico
  async obterResumoEstatisticas() {
    try {
      const response = await api.get('/contas/resumo/estatisticas')
      return response.data
    } catch (error) {
      console.error('Erro ao obter resumo de contas:', error)
      throw error
    }
  },

  // Listar bancos únicos
  async listarBancosUnicos() {
    try {
      const response = await api.get('/contas/bancos/lista')
      return response.data
    } catch (error) {
      console.error('Erro ao listar bancos:', error)
      throw error
    }
  },

  // Listar lançamentos de uma conta
  async listarLancamentosConta(contaId, filtros = {}) {
    try {
      const params = new URLSearchParams()
      
      if (filtros.skip) {
        params.append('skip', filtros.skip)
      }
      if (filtros.limit) {
        params.append('limit', filtros.limit)
      }
      
      const url = params.toString() ? 
        `/contas/${contaId}/lancamentos?${params.toString()}` : 
        `/contas/${contaId}/lancamentos`
      
      const response = await api.get(url)
      return response.data
    } catch (error) {
      console.error('Erro ao listar lançamentos da conta:', error)
      throw error
    }
  },

  // Métodos auxiliares para opções
  getTiposContaOptions() {
    return [
      { label: 'Todos', value: '' },
      { label: 'Conta Corrente', value: 'CORRENTE' },
      { label: 'Poupança', value: 'POUPANCA' },
      { label: 'Investimento', value: 'INVESTIMENTO' }
    ]
  },

  getStatusOptions() {
    return [
      { label: 'Todas', value: '' },
      { label: 'Ativas', value: 'true' },
      { label: 'Inativas', value: 'false' }
    ]
  },

  // Lista de bancos brasileiros comuns
  getBancosComuns() {
    return [
      'Banco do Brasil',
      'Bradesco',
      'Itaú',
      'Santander',
      'Caixa Econômica Federal',
      'BTG Pactual',
      'Nubank',
      'Inter',
      'C6 Bank',
      'Original',
      'Safra',
      'Votorantim',
      'PAN',
      'Pine',
      'Neon',
      '99Pay',
      'PicPay',
      'Mercado Pago',
      'XP Investimentos',
      'Clear',
      'Rico',
      'Modalmais',
      'Easynvest',
      'Avenue'
    ].sort()
  },

  // Validações
  validarConta(contaData) {
    const erros = []
    
    if (!contaData.nome || contaData.nome.trim() === '') {
      erros.push('Nome da conta é obrigatório')
    }
    
    if (!contaData.banco || contaData.banco.trim() === '') {
      erros.push('Banco é obrigatório')
    }
    
    if (!contaData.tipo_conta) {
      erros.push('Tipo de conta é obrigatório')
    }
    
    if (contaData.numero_conta && contaData.numero_conta.length < 4) {
      erros.push('Número da conta deve ter pelo menos 4 dígitos')
    }
    
    if (contaData.agencia && contaData.agencia.length < 3) {
      erros.push('Agência deve ter pelo menos 3 dígitos')
    }
    
    if (contaData.saldo_inicial === undefined || contaData.saldo_inicial === null) {
      erros.push('Saldo inicial é obrigatório')
    }
    
    return erros
  },

  // Formatadores
  formatarTipoConta(tipo) {
    const tipoMap = {
      'CORRENTE': { label: 'Conta Corrente', icon: 'mdi-credit-card', color: 'primary' },
      'POUPANCA': { label: 'Poupança', icon: 'mdi-piggy-bank', color: 'success' },
      'INVESTIMENTO': { label: 'Investimento', icon: 'mdi-trending-up', color: 'warning' }
    }
    
    return tipoMap[tipo] || { label: tipo, icon: 'mdi-bank', color: 'grey' }
  },

  formatarStatusConta(ativa) {
    return ativa === 'true' || ativa === true ? 
      { label: 'Ativa', color: 'success', icon: 'mdi-check-circle' } :
      { label: 'Inativa', color: 'error', icon: 'mdi-close-circle' }
  },

  formatarSaldo(saldo) {
    if (saldo === undefined || saldo === null) return 'R$ 0,00'
    
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(saldo)
  },

  getCorSaldo(saldo) {
    if (saldo > 0) return 'success'
    if (saldo < 0) return 'error'
    return 'warning'
  },

  // Utilitários
  calcularSaldoTotal(contas) {
    if (!Array.isArray(contas)) return 0
    return contas
      .filter(conta => conta.ativa === 'true' || conta.ativa === true)
      .reduce((total, conta) => total + (conta.saldo_atual || 0), 0)
  },

  agruparPorBanco(contas) {
    if (!Array.isArray(contas)) return {}
    
    return contas.reduce((grupos, conta) => {
      const banco = conta.banco
      if (!grupos[banco]) {
        grupos[banco] = []
      }
      grupos[banco].push(conta)
      return grupos
    }, {})
  },

  formatarNumeroConta(numero, agencia) {
    if (!numero) return 'N/A'
    
    let formatado = numero
    if (agencia) {
      formatado = `${agencia} / ${numero}`
    }
    
    return formatado
  }
} 