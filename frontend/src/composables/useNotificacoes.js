import { ref } from 'vue'

export function useNotificacoes() {
  const notificacoes = ref([])
  const addNotificacao = (msg) => {
    notificacoes.value.push({ msg, date: new Date() })
  }
  return {
    notificacoes,
    addNotificacao
  }
} 