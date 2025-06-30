import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'

// Vuetify
import 'vuetify/styles'
import './css/variables.scss'
import './css/app.scss'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

import App from './App.vue'

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
    'secondary-darken-1': '#388E3C',
    'secondary-darken-2': '#2E7D32',
    accent: '#FF6F00',
    error: '#E53935',
    info: '#1E88E5',
    success: '#43A047',
    warning: '#FB8C00',
    background: '#FAFAFA',
    surface: '#FFFFFF',
    'surface-variant': '#F8F9FA',
    'on-surface': '#212121',
    'on-primary': '#FFFFFF',
    'on-secondary': '#FFFFFF',
    'on-background': '#212121',
    'on-error': '#FFFFFF',
    'on-info': '#FFFFFF',
    'on-success': '#FFFFFF',
    'on-warning': '#000000'
  }
}

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'biuaiTheme',
    themes: {
      biuaiTheme
    }
  },
  defaults: {
    VBtn: {
      style: 'text-transform: none; font-weight: 600;',
      rounded: 'lg'
    },
    VCard: {
      elevation: 2,
      rounded: 'lg'
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable'
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable'
    },
    VTextarea: {
      variant: 'outlined',
      density: 'comfortable'
    }
  }
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(vuetify)

app.mount('#app') 