import FIIDashboard from './components/FIIDashboard.vue'
import { useFIIs } from './composables/useFIIs'
import { createFIIsStore } from './store'

export default {
  install: (app) => {
    // Registrar componentes globais
    app.component('FIIDashboard', FIIDashboard)
    
    // Registrar store
    const store = createFIIsStore()
    app.provide('fiisStore', store)
    
    // Registrar composables
    app.config.globalProperties.$fiis = useFIIs()
  }
} 