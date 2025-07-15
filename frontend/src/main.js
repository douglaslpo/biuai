import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import { loadFonts } from './plugins/webfontloader'
import router from './router'

// Importar módulo MyFIIs
import MyFIIs from '@/modules/myfiis'

// Vuetify
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import 'vuetify/styles'

// Custom styles
import '@/css/app.scss'
import '@/css/variables.scss'

// Tema personalizado BIUAI completo
const biuaiTheme = {
  dark: false,
  colors: {
    primary: '#1976D2',
    'primary-lighten-1': '#42A5F5',
    'primary-lighten-2': '#64B5F6',
    'primary-darken-1': '#1565C0',
    'primary-darken-2': '#0D47A1',
    secondary: '#43A047',
    'secondary-lighten-1': '#66BB6A',
    'secondary-lighten-2': '#81C784',
    'secondary-darken-1': '#2E7D32',
    'secondary-darken-2': '#1B5E20',
    accent: '#FF5722',
    error: '#FF5252',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FFC107'
  }
}

// Configuração do Vuetify
const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'biuaiTheme',
    themes: {
      biuaiTheme
    }
  }
})

// Criar e configurar app
const app = createApp(App)

// Plugins e configurações
app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(MyFIIs)

// Carregar fontes
loadFonts()

// Montar app
app.mount('#app') 