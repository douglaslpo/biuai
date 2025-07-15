// Funções de formatação para o módulo MyFIIs

/**
 * Formata um valor numérico para moeda (BRL)
 * @param {number} valor - Valor a ser formatado
 * @returns {string} Valor formatado
 */
export function formatarMoeda(valor) {
  if (valor === null || valor === undefined) return 'R$ 0,00'
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor)
}

/**
 * Formata um valor numérico para percentual
 * @param {number} valor - Valor a ser formatado
 * @returns {string} Valor formatado
 */
export function formatarPercentual(valor) {
  if (valor === null || valor === undefined) return '0%'
  return new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(valor / 100)
}

/**
 * Formata um número com separadores de milhar
 * @param {number} valor - Valor a ser formatado
 * @returns {string} Valor formatado
 */
export function formatarNumero(valor) {
  if (valor === null || valor === undefined) return '0'
  return new Intl.NumberFormat('pt-BR').format(valor)
}

export const formatDate = (date) => {
  if (!date) return ''
  return new Intl.DateTimeFormat('pt-BR').format(new Date(date))
}

export const formatNumber = (value) => {
  if (!value) return '0'
  return new Intl.NumberFormat('pt-BR').format(value)
}

export function formatCurrency(value) {
  if (typeof value !== 'number') return value
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function formatPercentage(value) {
  if (typeof value !== 'number') return value
  return value.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) + '%'
} 