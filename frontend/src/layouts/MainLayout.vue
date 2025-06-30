<template>
  <v-app>
    <!-- App Bar -->
    <v-app-bar
      :elevation="2"
      color="primary"
      dark
      app
      clipped-left
    >
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      
      <!-- Logo BIUAI -->
      <div class="d-flex align-center">
        <v-img
          alt="BIUAI Logo"
          class="shrink mr-2"
          contain
          :src="logoUrl"
          transition="scale-transition"
          width="40"
        />
        <v-toolbar-title class="text-h5 font-weight-bold">
          BIUAI
        </v-toolbar-title>
      </div>

      <v-spacer />

      <!-- Search -->
      <v-text-field
        v-model="searchQuery"
        append-inner-icon="mdi-magnify"
        label="Buscar..."
        single-line
        hide-details
        density="compact"
        variant="solo"
        class="mx-4"
        style="max-width: 300px;"
      />

      <!-- Notifications -->
      <v-btn icon size="large">
        <v-badge
          :content="notificationCount"
          :value="notificationCount"
          color="error"
          overlap
        >
          <v-icon>mdi-bell</v-icon>
        </v-badge>
      </v-btn>

      <!-- User Menu -->
      <v-menu offset-y>
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            icon
            size="large"
          >
            <v-avatar size="36" color="secondary">
              <v-icon>mdi-account</v-icon>
            </v-avatar>
          </v-btn>
        </template>
        
        <v-list>
          <v-list-item>
            <v-list-item-title>{{ user?.full_name || 'Usuário' }}</v-list-item-title>
            <v-list-item-subtitle>{{ user?.email }}</v-list-item-subtitle>
          </v-list-item>
          
          <v-divider />
          
          <v-list-item @click="goToProfile">
            <v-list-item-title>
              <v-icon start>mdi-account-circle</v-icon>
              Perfil
            </v-list-item-title>
          </v-list-item>
          
          <v-list-item @click="goToSettings">
            <v-list-item-title>
              <v-icon start>mdi-cog</v-icon>
              Configurações
            </v-list-item-title>
          </v-list-item>
          
          <v-divider />
          
          <v-list-item @click="logout">
            <v-list-item-title class="text-error">
              <v-icon start>mdi-logout</v-icon>
              Sair
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Navigation Drawer -->
    <v-navigation-drawer
      v-model="drawer"
      app
      clipped
      :width="280"
      color="surface"
    >
      <!-- User Info -->
      <v-list-item class="pa-4">
        <template v-slot:prepend>
          <v-avatar size="48" color="primary">
            <v-icon size="24">mdi-account</v-icon>
          </v-avatar>
        </template>
        
        <v-list-item-title class="font-weight-bold">
          {{ user?.full_name || 'Usuário' }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ user?.email }}
        </v-list-item-subtitle>
      </v-list-item>

      <v-divider />

      <!-- Navigation Menu -->
      <v-list density="compact" nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          :subtitle="item.subtitle"
          color="primary"
        />
      </v-list>

      <v-divider class="my-2" />

      <!-- Tools Section -->
      <v-list-subheader>FERRAMENTAS</v-list-subheader>
      <v-list density="compact" nav>
        <v-list-item
          v-for="tool in toolItems"
          :key="tool.title"
          :to="tool.to"
          :prepend-icon="tool.icon"
          :title="tool.title"
          color="primary"
        />
      </v-list>

      <!-- System Status -->
      <template v-slot:append>
        <v-divider />
        <v-list-item class="pa-4">
          <v-chip
            :color="systemStatus.color"
            variant="elevated"
            size="small"
            class="ma-1"
          >
            <v-icon start size="12">{{ systemStatus.icon }}</v-icon>
            {{ systemStatus.text }}
          </v-chip>
        </v-list-item>
      </template>
    </v-navigation-drawer>

    <!-- Main Content -->
    <v-main>
      <v-container fluid class="pa-6">
        <router-view />
      </v-container>
    </v-main>

    <!-- Footer -->
    <v-footer
      app
      color="surface"
      class="text-center pa-4"
    >
      <div class="d-flex justify-space-between align-center w-100">
        <div class="text-caption">
          © 2024 BIUAI - Business Intelligence Unity with AI
        </div>
        <div class="text-caption">
          Versão {{ version }} | API: {{ apiStatus }}
        </div>
      </div>
    </v-footer>

    <!-- Chatbot Modal -->
    <ChatbotModal />
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ChatbotModal from '@/components/ChatbotModal.vue'

// Stores
const authStore = useAuthStore()
const router = useRouter()

// Data
const drawer = ref(true)
const searchQuery = ref('')
const notificationCount = ref(3)
const version = ref('1.0.0')
const apiStatus = ref('Online')

// Logo URL (você pode colocar o logo em public/images/)
const logoUrl = ref('/images/biuai-logo.svg')

// Computed
const user = computed(() => authStore.user)

const systemStatus = computed(() => ({
  color: 'success',
  icon: 'mdi-check-circle',
  text: 'Sistema Online'
}))

// Menu Items
const menuItems = ref([
  {
    title: 'Dashboard',
    subtitle: 'Visão geral',
    icon: 'mdi-view-dashboard',
    to: '/dashboard'
  },
  {
    title: 'Lançamentos',
    subtitle: 'Receitas e despesas',
    icon: 'mdi-cash-multiple',
    to: '/lancamentos'
  },
  {
    title: 'Categorias',
    subtitle: 'Organizar gastos',
    icon: 'mdi-tag-multiple',
    to: '/categorias'
  },
  {
    title: 'Relatórios',
    subtitle: 'Análises financeiras',
    icon: 'mdi-chart-line',
    to: '/relatorios'
  },
  {
    title: 'Metas',
    subtitle: 'Objetivos financeiros',
    icon: 'mdi-target',
    to: '/metas'
  },
  {
    title: 'Contas',
    subtitle: 'Contas bancárias',
    icon: 'mdi-bank',
    to: '/contas'
  }
])

const toolItems = computed(() => {
  const items = [
    {
      title: 'Perfil',
      icon: 'mdi-account',
      to: '/profile'
    }
  ]
  
  // Adicionar itens administrativos apenas para admins
  if (user.value?.is_superuser) {
    items.push(
      {
        title: 'Chatbot Admin',
        icon: 'mdi-robot',
        to: '/admin/chatbot'
      },
      {
        title: 'Importar Dados',
        icon: 'mdi-database-import',
        to: '/admin/importar-dados'
      },
      {
        title: 'Backup',
        icon: 'mdi-backup-restore',
        to: '/admin/backup'
      },
      {
        title: 'API Docs',
        icon: 'mdi-api',
        to: '/admin/api-docs'
      },
      {
        title: 'Logs do Sistema',
        icon: 'mdi-math-log',
        to: '/admin/logs'
      }
    )
  }
  
  return items
})

// Methods
const logout = async () => {
  await authStore.logout()
  router.push('/login')
}

const goToProfile = () => {
  router.push('/profile')
}

const goToSettings = () => {
  router.push('/settings')
}

// Lifecycle
onMounted(async () => {
  // Verificar status da API
  try {
    // Aqui você pode fazer uma chamada para verificar o status da API
    apiStatus.value = 'Online'
  } catch (error) {
    apiStatus.value = 'Offline'
  }
})
</script>

<style scoped>
.v-toolbar-title {
  letter-spacing: 1px;
}
</style> 