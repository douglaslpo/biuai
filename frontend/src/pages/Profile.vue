<template>
  <v-container fluid class="pa-6">
    <div class="d-flex align-center mb-6">
      <v-icon color="primary" size="32" class="mr-3">mdi-account</v-icon>
      <div>
        <h1 class="text-h4 font-weight-bold">Meu Perfil</h1>
        <p class="text-subtitle-1 text-medium-emphasis mb-0">
          Gerencie suas informações pessoais e configurações
        </p>
      </div>
    </div>

    <v-row>
      <v-col cols="12" md="8">
        <BaseCard title="Informações Pessoais" icon="mdi-account-edit">
          <v-form @submit.prevent="updateProfile">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="profileForm.full_name"
                  label="Nome Completo"
                  prepend-inner-icon="mdi-account"
                  variant="outlined"
                  :rules="[v => !!v || 'Nome é obrigatório']"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="profileForm.email"
                  label="Email"
                  type="email"
                  prepend-inner-icon="mdi-email"
                  variant="outlined"
                  readonly
                />
              </v-col>
            </v-row>
            
            <v-btn
              type="submit"
              color="primary"
              variant="elevated"
              :loading="updating"
            >
              <v-icon start>mdi-content-save</v-icon>
              Salvar Alterações
            </v-btn>
          </v-form>
        </BaseCard>

        <BaseCard title="Alterar Senha" icon="mdi-lock" class="mt-4">
          <v-form @submit.prevent="changePassword">
            <v-text-field
              v-model="passwordForm.current_password"
              label="Senha Atual"
              type="password"
              prepend-inner-icon="mdi-lock"
              variant="outlined"
              :rules="[v => !!v || 'Senha atual é obrigatória']"
              class="mb-3"
            />
            
            <v-text-field
              v-model="passwordForm.new_password"
              label="Nova Senha"
              type="password"
              prepend-inner-icon="mdi-lock-plus"
              variant="outlined"
              :rules="passwordRules"
              class="mb-3"
            />
            
            <v-text-field
              v-model="passwordForm.confirm_password"
              label="Confirmar Nova Senha"
              type="password"
              prepend-inner-icon="mdi-lock-check"
              variant="outlined"
              :rules="confirmPasswordRules"
              class="mb-3"
            />
            
            <v-btn
              type="submit"
              color="warning"
              variant="elevated"
              :loading="changingPassword"
            >
              <v-icon start>mdi-key-change</v-icon>
              Alterar Senha
            </v-btn>
          </v-form>
        </BaseCard>
      </v-col>

      <v-col cols="12" md="4">
        <BaseCard title="Informações da Conta" icon="mdi-information">
          <v-list density="compact">
            <v-list-item
              prepend-icon="mdi-account-circle"
              title="Tipo de Conta"
              :subtitle="user?.is_superuser ? 'Administrador' : 'Usuário'"
            />
            <v-list-item
              prepend-icon="mdi-calendar"
              title="Membro desde"
              :subtitle="formatDate(user?.created_at)"
            />
            <v-list-item
              prepend-icon="mdi-clock"
              title="Última atualização"
              :subtitle="formatDate(user?.updated_at)"
            />
            <v-list-item
              prepend-icon="mdi-check-circle"
              title="Status"
              :subtitle="user?.is_active ? 'Ativo' : 'Inativo'"
            />
          </v-list>
        </BaseCard>

        <BaseCard title="Ações da Conta" icon="mdi-cog" class="mt-4">
          <div class="d-flex flex-column gap-2">
            <v-btn
              color="error"
              variant="outlined"
              size="small"
              @click="showDeleteDialog = true"
            >
              <v-icon start>mdi-delete</v-icon>
              Excluir Conta
            </v-btn>
          </div>
        </BaseCard>
      </v-col>
    </v-row>

    <!-- Dialog de Confirmação de Exclusão -->
    <v-dialog v-model="showDeleteDialog" max-width="500">
      <BaseCard title="Excluir Conta" icon="mdi-alert">
        <p class="mb-4">
          Tem certeza que deseja excluir sua conta? 
          <strong>Esta ação não pode ser desfeita</strong> e todos os seus dados serão perdidos.
        </p>
        
        <v-text-field
          v-model="confirmText"
          label='Digite "EXCLUIR" para confirmar'
          variant="outlined"
          class="mb-4"
        />
        
        <template #actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="showDeleteDialog = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="error"
            :disabled="confirmText !== 'EXCLUIR'"
            @click="deleteAccount"
          >
            Excluir Conta
          </v-btn>
        </template>
      </BaseCard>
    </v-dialog>

    <!-- Snackbar -->
    <v-snackbar
      v-model="showNotification"
      :color="notificationType"
      timeout="5000"
    >
      {{ notificationMessage }}
      <template v-slot:actions>
        <v-btn
          color="white"
          variant="text"
          @click="showNotification = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BaseCard from '@/components/base/BaseCard.vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/boot/axios'

// Stores
const authStore = useAuthStore()
const router = useRouter()

// Estado reativo
const updating = ref(false)
const changingPassword = ref(false)
const showDeleteDialog = ref(false)
const confirmText = ref('')
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref('info')

// Dados do usuário
const user = computed(() => authStore.user)

// Formulários
const profileForm = reactive({
  full_name: '',
  email: ''
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

// Regras de validação
const passwordRules = [
  v => !!v || 'Nova senha é obrigatória',
  v => (v && v.length >= 8) || 'Senha deve ter pelo menos 8 caracteres'
]

const confirmPasswordRules = computed(() => [
  v => !!v || 'Confirmação de senha é obrigatória',
  v => v === passwordForm.new_password || 'Senhas não conferem'
])

// Métodos
const updateProfile = async () => {
  updating.value = true
  
  try {
    const result = await authStore.updateProfile(profileForm)
    
    if (result.success) {
      showNotificationMessage('Perfil atualizado com sucesso!', 'success')
    } else {
      showNotificationMessage(result.error || 'Erro ao atualizar perfil', 'error')
    }
  } catch (error) {
    showNotificationMessage('Erro ao atualizar perfil: ' + error.message, 'error')
  } finally {
    updating.value = false
  }
}

const changePassword = async () => {
  changingPassword.value = true
  
  try {
    const response = await api.put('/api/v1/auth/change-password', {
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password
    })
    
    if (response.data.success) {
      showNotificationMessage('Senha alterada com sucesso!', 'success')
      
      // Limpar formulário
      passwordForm.current_password = ''
      passwordForm.new_password = ''
      passwordForm.confirm_password = ''
    }
  } catch (error) {
    showNotificationMessage('Erro ao alterar senha: ' + error.message, 'error')
  } finally {
    changingPassword.value = false
  }
}

const deleteAccount = async () => {
  try {
    await api.delete('/api/v1/users/me')
    
    showNotificationMessage('Conta excluída com sucesso!', 'info')
    
    // Fazer logout e redirecionar
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    showNotificationMessage('Erro ao excluir conta: ' + error.message, 'error')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('pt-BR')
}

const showNotificationMessage = (message, type = 'info') => {
  notificationMessage.value = message
  notificationType.value = type
  showNotification.value = true
}

// Lifecycle
onMounted(() => {
  if (user.value) {
    profileForm.full_name = user.value.full_name || ''
    profileForm.email = user.value.email || ''
  }
})
</script>

<style lang="scss" scoped>
.v-card {
  border-radius: 12px;
}
</style> 