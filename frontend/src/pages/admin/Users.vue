<template>
  <div class="users-admin-page">
    <!-- Page Header -->
    <PageHeader
      title="Gerenciamento de Usuários"
      subtitle="Administre usuários do sistema, permissões e acessos"
      icon="mdi-account-group"
    >
      <template #actions>
        <v-btn
          color="primary"
          size="large"
          variant="elevated"
          prepend-icon="mdi-account-plus"
          @click="showCreateDialog = true"
          class="mr-2"
        >
          Novo Usuário
        </v-btn>
        
        <v-btn
          color="secondary"
          size="large"
          variant="outlined"
          icon="mdi-refresh"
          :loading="loading"
          @click="refresh"
        />
      </template>

      <template #metrics>
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Total de Usuários"
              :value="metrics.totalUsuarios"
              icon="mdi-account-group"
              color="primary"
            />
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Usuários Ativos"
              :value="metrics.usuariosAtivos"
              icon="mdi-account-check"
              color="success"
            />
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Administradores"
              :value="metrics.administradores"
              icon="mdi-shield-account"
              color="warning"
            />
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <MetricCard
              label="Último Login"
              :value="metrics.ultimoLogin"
              icon="mdi-clock-outline"
              color="info"
            />
          </v-col>
        </v-row>
      </template>
    </PageHeader>

    <!-- Filters Card -->
    <BaseCard class="mb-6" elevation="2">
      <template #title>
        <v-icon icon="mdi-filter" class="mr-2" />
        Filtros e Pesquisa
      </template>
      
      <v-row>
        <v-col cols="12" md="3">
          <v-select
            v-model="filters.is_active"
            :items="statusOptions"
            label="Status"
            density="comfortable"
            variant="outlined"
            clearable
          />
        </v-col>
        
        <v-col cols="12" md="3">
          <v-select
            v-model="filters.is_superuser"
            :items="typeOptions"
            label="Tipo de Usuário"
            density="comfortable"
            variant="outlined"
            clearable
          />
        </v-col>
        
        <v-col cols="12" md="4">
          <v-text-field
            v-model="searchQuery"
            label="Buscar usuários..."
            density="comfortable"
            variant="outlined"
            prepend-inner-icon="mdi-magnify"
            clearable
            @input="setSearch"
          />
        </v-col>
        
        <v-col cols="12" md="2">
          <v-btn
            color="primary"
            variant="outlined"
            block
            @click="clearFilters"
          >
            Limpar
          </v-btn>
        </v-col>
      </v-row>
    </BaseCard>

    <!-- Users Table -->
    <BaseCard elevation="2">
      <template #title>
        <div class="d-flex align-center justify-space-between w-100">
          <div class="d-flex align-center">
            <v-icon icon="mdi-table" class="mr-3" />
            <span class="text-h6">Lista de Usuários</span>
          </div>
          <v-chip 
            :color="filteredData.length > 0 ? 'success' : 'warning'" 
            variant="tonal"
          >
            {{ filteredData.length }} usuário{{ filteredData.length !== 1 ? 's' : '' }}
          </v-chip>
        </div>
      </template>
      
      <v-data-table
        :headers="headers"
        :items="paginatedData"
        :loading="loading"
        item-key="id"
        :items-per-page="itemsPerPage"
        hide-default-footer
        class="users-table"
      >
        <!-- Avatar -->
        <template #item.avatar="{ item }">
          <v-avatar size="40" class="ma-2">
            <v-img v-if="item.avatar" :src="item.avatar" />
            <v-icon v-else size="24">mdi-account</v-icon>
          </v-avatar>
        </template>

        <!-- Status -->
        <template #item.is_active="{ item }">
          <v-chip
            :color="item.is_active ? 'success' : 'error'"
            variant="elevated"
            size="small"
          >
            <v-icon 
              :icon="item.is_active ? 'mdi-check' : 'mdi-close'" 
              size="small" 
              class="mr-1"
            />
            {{ item.is_active ? 'Ativo' : 'Inativo' }}
          </v-chip>
        </template>

        <!-- Tipo -->
        <template #item.is_superuser="{ item }">
          <v-chip
            :color="item.is_superuser ? 'error' : 'primary'"
            variant="tonal"
            size="small"
          >
            <v-icon 
              :icon="item.is_superuser ? 'mdi-shield-account' : 'mdi-account'" 
              size="small" 
              class="mr-1"
            />
            {{ item.is_superuser ? 'Admin' : 'Usuário' }}
          </v-chip>
        </template>

        <!-- Último acesso -->
        <template #item.last_login="{ item }">
          <span :title="formatDateTime(item.last_login)">
            {{ formatRelativeTime(item.last_login) }}
          </span>
        </template>

        <!-- Ações -->
        <template #item.actions="{ item }">
          <div class="action-buttons">
            <v-btn
              icon="mdi-eye"
              size="small"
              variant="text"
              color="primary"
              @click="viewUser(item)"
            />
            <v-btn
              icon="mdi-pencil"
              size="small"
              variant="text"
              color="primary"
              @click="editUser(item)"
            />
            <v-btn
              :icon="item.is_active ? 'mdi-account-off' : 'mdi-account-check'"
              size="small"
              variant="text"
              :color="item.is_active ? 'warning' : 'success'"
              @click="toggleUserStatus(item)"
            />
            <v-btn
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              @click="confirmDelete(item)"
              :disabled="item.is_superuser && item.id === currentUser?.id"
            />
          </div>
        </template>
      </v-data-table>

      <!-- Custom Pagination -->
      <div class="d-flex justify-center pa-4">
        <v-pagination
          v-model="currentPage"
          :length="totalPages"
          :total-visible="7"
          @update:model-value="goToPage"
        />
      </div>
    </BaseCard>

    <!-- User Dialog -->
    <UserDialog
      v-model="showCreateDialog"
      :user="editingUser"
      :loading="dialogLoading"
      @save="handleSave"
      @cancel="handleCancel"
    />

    <!-- User Details Dialog -->
    <UserDetailsDialog
      v-model="showDetailsDialog"
      :user="viewingUser"
      @close="showDetailsDialog = false"
    />

    <!-- Delete Confirmation -->
    <ConfirmDialog
      v-model="showDeleteDialog"
      title="Confirmar Exclusão"
      :message="`Tem certeza que deseja excluir o usuário '${deletingUser?.full_name}'? Esta ação não pode ser desfeita.`"
      confirm-text="Excluir"
      confirm-color="error"
      type="error"
      @confirm="handleDelete"
      @cancel="showDeleteDialog = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePageData } from '@/composables/usePageData'
import { useNotifications } from '@/composables/useNotifications'
import { useAuthStore } from '@/stores/auth'
import { usersService } from '@/services/admin/users'

// Components
import PageHeader from '@/components/base/PageHeader.vue'
import MetricCard from '@/components/base/MetricCard.vue'
import BaseCard from '@/components/base/BaseCard.vue'
import UserDialog from '@/components/admin/UserDialog.vue'
import UserDetailsDialog from '@/components/admin/UserDetailsDialog.vue'
import ConfirmDialog from '@/components/modals/ConfirmDialog.vue'

// Stores & Composables
const authStore = useAuthStore()
const {
  data: users,
  filteredData,
  paginatedData,
  loading,
  isEmpty,
  searchQuery,
  filters,
  currentPage,
  totalPages,
  itemsPerPage,
  setSearch,
  clearFilters,
  refresh,
  goToPage,
  addItem,
  updateItem,
  removeItem
} = usePageData({
  fetchFn: usersService.list,
  autoFetch: true,
  pageSize: 15
})

const { showActionSuccess, showActionError } = useNotifications()

// Local state
const showCreateDialog = ref(false)
const showDetailsDialog = ref(false)
const showDeleteDialog = ref(false)
const editingUser = ref(null)
const viewingUser = ref(null)
const deletingUser = ref(null)
const dialogLoading = ref(false)

// Current user
const currentUser = computed(() => authStore.user)

// Table headers
const headers = [
  { title: '', key: 'avatar', sortable: false, width: '80px' },
  { title: 'Nome', key: 'full_name', sortable: true },
  { title: 'Email', key: 'email', sortable: true },
  { title: 'Status', key: 'is_active', sortable: true },
  { title: 'Tipo', key: 'is_superuser', sortable: true },
  { title: 'Último Acesso', key: 'last_login', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false, align: 'center' }
]

// Options
const statusOptions = [
  { title: 'Ativo', value: true },
  { title: 'Inativo', value: false }
]

const typeOptions = [
  { title: 'Administrador', value: true },
  { title: 'Usuário', value: false }
]

// Computed
const metrics = computed(() => {
  const total = users.value.length
  const ativos = users.value.filter(u => u.is_active).length
  const admins = users.value.filter(u => u.is_superuser).length
  
  // Último login mais recente
  const lastLogins = users.value
    .filter(u => u.last_login)
    .sort((a, b) => new Date(b.last_login) - new Date(a.last_login))
  
  const ultimoLogin = lastLogins.length > 0 
    ? formatRelativeTime(lastLogins[0].last_login)
    : 'N/A'

  return {
    totalUsuarios: total,
    usuariosAtivos: ativos,
    administradores: admins,
    ultimoLogin
  }
})

// Methods
const editUser = (user) => {
  editingUser.value = { ...user }
  showCreateDialog.value = true
}

const viewUser = (user) => {
  viewingUser.value = user
  showDetailsDialog.value = true
}

const confirmDelete = (user) => {
  deletingUser.value = user
  showDeleteDialog.value = true
}

const toggleUserStatus = async (user) => {
  try {
    const updated = await usersService.toggleStatus(user.id, !user.is_active)
    updateItem(user.id, updated)
    showActionSuccess('update', `Status do usuário`)
  } catch (error) {
    showActionError('update', 'status do usuário', error.message)
  }
}

const handleSave = async (userData) => {
  try {
    dialogLoading.value = true
    
    if (editingUser.value?.id) {
      // Update
      const updated = await usersService.update(editingUser.value.id, userData)
      updateItem(editingUser.value.id, updated)
      showActionSuccess('update', 'Usuário')
    } else {
      // Create
      const created = await usersService.create(userData)
      addItem(created)
      showActionSuccess('create', 'Usuário')
    }
    
    handleCancel()
    
  } catch (error) {
    showActionError(editingUser.value?.id ? 'update' : 'create', 'usuário', error.message)
  } finally {
    dialogLoading.value = false
  }
}

const handleCancel = () => {
  showCreateDialog.value = false
  editingUser.value = null
  dialogLoading.value = false
}

const handleDelete = async () => {
  try {
    await usersService.delete(deletingUser.value.id)
    removeItem(deletingUser.value.id)
    showActionSuccess('delete', 'Usuário')
    
  } catch (error) {
    showActionError('delete', 'usuário', error.message)
  } finally {
    showDeleteDialog.value = false
    deletingUser.value = null
  }
}

const formatDateTime = (date) => {
  if (!date) return 'Nunca'
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date))
}

const formatRelativeTime = (date) => {
  if (!date) return 'Nunca'
  
  const now = new Date()
  const past = new Date(date)
  const diffMs = now - past
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Hoje'
  if (diffDays === 1) return 'Ontem'
  if (diffDays < 7) return `${diffDays} dias atrás`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} semanas atrás`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} meses atrás`
  return `${Math.floor(diffDays / 365)} anos atrás`
}

// Lifecycle
onMounted(() => {
  // Additional setup if needed
})
</script>

<style scoped>
.users-admin-page {
  padding: 0;
}

.users-table {
  border-radius: 8px;
}

.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
}

/* Responsividade */
@media (max-width: 768px) {
  .users-admin-page :deep(.header-actions) {
    flex-direction: column;
    gap: 8px;
  }
  
  .users-admin-page :deep(.header-actions .v-btn) {
    width: 100%;
  }
}</style> 