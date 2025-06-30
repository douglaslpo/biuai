import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

// Tema personalizado BIUAI
const biuaiTheme = {
  dark: false,
  colors: {
    primary: '#1976D2',      // Azul principal do BIUAI
    secondary: '#424242',    // Cinza escuro
    accent: '#82B1FF',       // Azul claro
    error: '#FF5252',        // Vermelho para erros
    info: '#2196F3',         // Azul para informações
    success: '#4CAF50',      // Verde para sucesso
    warning: '#FFC107',      // Amarelo para avisos
    background: '#FAFAFA',   // Fundo claro
    surface: '#FFFFFF',      // Superfície
    'on-primary': '#FFFFFF',
    'on-secondary': '#FFFFFF',
    'on-background': '#000000',
    'on-surface': '#000000',
    'primary-darken-1': '#1565C0',
    'secondary-darken-1': '#333333'
  }
}

const vuetify = createVuetify({
  theme: {
    defaultTheme: 'biuaiTheme',
    themes: {
      biuaiTheme
    }
  },
  defaults: {
    VCard: {
      elevation: 3,
      rounded: 'lg'
    },
    VBtn: {
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
    }
  }
})

export default ({ app }) => {
  app.use(vuetify)
} 