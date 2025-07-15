<template>
  <div class="gestor-acessos-page">
    <PageHeader
      title="Gestor de Acessos"
      subtitle="Administre acessos, permissões e limites do seu SaaS"
      icon="mdi-account-key"
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
          Novo Acesso
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
          <v-col cols="12" sm="6" md="4">
            <MetricCard label="Total de Usuários" :value="metrics.totalUsuarios" icon="mdi-account-group" color="primary" />
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <MetricCard label="Admins" :value="metrics.admins" icon="mdi-shield-account" color="warning" />
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <MetricCard label="Limite de Acessos" :value="metrics.limiteAcessos" icon="mdi-account-multiple-check" color="info" />
          </v-col>
        </v-row>
      </template>
    </PageHeader>
    <BaseCard class="mb-6" elevation="2">
      <template #title>
        <v-icon icon="mdi-tune" class="mr-2" />
        Parâmetros de Limite de Acesso
      </template>
      <v-row>
        <v-col cols="12" md="6">
          <v-text-field
            v-model="limiteAcessos"
            label="Máximo de acessos permitidos"
            type="number"
            min="1"
            variant="outlined"
          />
        </v-col>
        <v-col cols="12" md="6">
          <v-btn color="primary" @click="salvarLimite">Salvar Limite</v-btn>
        </v-col>
      </v-row>
    </BaseCard>
    <BaseCard elevation="2">
      <template #title>
        <div class="d-flex align-center justify-space-between w-100">
          <div class="d-flex align-center">
            <v-icon icon="mdi-table" class="mr-3" />
            <span class="text-h6">Lista de Acessos</span>
          </div>
        </div>
      </template>
      <v-data-table
        :headers="headers"
        :items="usuarios"
        :loading="loading"
        item-key="id"
        :items-per-page="15"
        hide-default-footer
        class="acessos-table"
      >
        <template #item.tipo="{ item }">
          <v-chip :color="item.is_superuser ? (item.is_master ? 'red' : 'warning') : 'primary'">
            {{ item.is_master ? 'Admin Master' : (item.is_superuser ? 'Admin' : 'Usuário') }}
          </v-chip>
        </template>
        <template #item.actions="{ item }">
          <div class="action-buttons">
            <v-btn icon="mdi-eye" size="small" variant="text" color="primary" @click="viewUser(item)" />
            <v-btn icon="mdi-pencil" size="small" variant="text" color="primary" @click="editUser(item)" />
            <v-btn :icon="item.is_active ? 'mdi-account-off' : 'mdi-account-check'" size="small" variant="text" :color="item.is_active ? 'warning' : 'success'" @click="toggleUserStatus(item)" />
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="confirmDelete(item)" :disabled="item.is_master" />
          </div>
        </template>
      </v-data-table>
    </BaseCard>
    <UserDialog v-model="showCreateDialog" :user="editingUser" :loading="dialogLoading" @save="handleSave" @cancel="handleCancel" />
    <UserDetailsDialog v-model="showDetailsDialog" :user="viewingUser" @close="showDetailsDialog = false" />
    <ConfirmDialog v-model="showDeleteDialog" title="Confirmar Exclusão" :message="`Tem certeza que deseja excluir o acesso '${deletingUser?.full_name}'? Esta ação não pode ser desfeita.`" confirm-text="Excluir" confirm-color="error" type="error" @confirm="handleDelete" @cancel="showDeleteDialog = false" />
  </div>
</template>

<script setup>
import UserDetailsDialog from '@/components/admin/UserDetailsDialog.vue'
import UserDialog from '@/components/admin/UserDialog.vue'
import BaseCard from '@/components/base/BaseCard.vue'
import MetricCard from '@/components/base/MetricCard.vue'
import PageHeader from '@/components/base/PageHeader.vue'
import ConfirmDialog from '@/components/modals/ConfirmDialog.vue'
import { computed, ref } from 'vue'

const usuarios = ref([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showDetailsDialog = ref(false)
const showDeleteDialog = ref(false)
const editingUser = ref(null)
const viewingUser = ref(null)
const deletingUser = ref(null)
const dialogLoading = ref(false)
const limiteAcessos = ref(10)

const headers = [
  { title: '', key: 'avatar', sortable: false, width: '80px' },
  { title: 'Nome', key: 'full_name', sortable: true },
  { title: 'Email', key: 'email', sortable: true },
  { title: 'Status', key: 'is_active', sortable: true },
  { title: 'Tipo', key: 'tipo', sortable: true },
  { title: 'Último Acesso', key: 'last_login', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false, align: 'center' }
]

const metrics = computed(() => ({
  totalUsuarios: usuarios.value.length,
  admins: usuarios.value.filter(u => u.is_superuser).length,
  limiteAcessos: limiteAcessos.value
}))

const viewUser = (user) => { viewingUser.value = user; showDetailsDialog.value = true }
const editUser = (user) => { editingUser.value = { ...user }; showCreateDialog.value = true }
const confirmDelete = (user) => { deletingUser.value = user; showDeleteDialog.value = true }
const toggleUserStatus = async (user) => {/* lógica de ativar/desativar */}
const handleSave = async (userData) => {/* lógica de salvar novo acesso */}
const handleCancel = () => { showCreateDialog.value = false; editingUser.value = null; dialogLoading.value = false }
const handleDelete = async () => {/* lógica de exclusão */}
const refresh = () => {/* lógica de refresh */}
const salvarLimite = () => {/* lógica para salvar limite de acessos */}
</script>

<style scoped>
.gestor-acessos-page { padding: 24px; }
.acessos-table { margin-top: 16px; }
.action-buttons > * { margin-right: 4px; }
</style> 