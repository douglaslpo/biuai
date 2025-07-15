<template>
  <div class="profile-page">
    <!-- Page Header -->
    <PageHeader
      title="Meu Perfil"
      subtitle="Gerencie suas informações pessoais e configurações da conta"
      icon="mdi-account-circle"
    >
      <template #actions>
        <v-btn
          color="primary"
          size="large"
          variant="elevated"
          prepend-icon="mdi-content-save"
          :loading="saving"
          :disabled="!hasChanges"
          @click="handleSave"
          class="mr-2"
        >
          Salvar Alterações
        </v-btn>
        
        <v-btn
          color="secondary"
          size="large"
          variant="outlined"
          prepend-icon="mdi-refresh"
          @click="resetForm"
        >
          Cancelar
        </v-btn>
      </template>
    </PageHeader>

    <!-- Profile Content -->
    <v-row>
      <!-- Avatar Section -->
      <v-col cols="12" md="4">
        <BaseCard elevation="2" class="text-center">
          <template #title>
            <v-icon icon="mdi-account-circle" class="mr-2" />
            Foto do Perfil
          </template>
          
          <div class="avatar-section py-6">
            <v-avatar size="120" class="mb-4">
              <v-img v-if="profileData.avatar" :src="profileData.avatar" />
              <v-icon v-else size="80" color="grey-lighten-1">mdi-account</v-icon>
            </v-avatar>
            
            <h3 class="text-h5 mb-2">{{ profileData.full_name || 'Usuário' }}</h3>
            <p class="text-body-2 text-medium-emphasis mb-4">{{ profileData.email }}</p>
            
            <v-btn
              color="primary"
              variant="outlined"
              prepend-icon="mdi-camera"
              @click="selectAvatar"
            >
              Alterar Foto
            </v-btn>
            
            <input
              ref="avatarInput"
              type="file"
              accept="image/*"
              style="display: none"
              @change="handleAvatarChange"
            />
          </div>
        </BaseCard>

        <!-- Account Info -->
        <BaseCard elevation="2" class="mt-6">
          <template #title>
            <v-icon icon="mdi-information" class="mr-2" />
            Informações da Conta
          </template>
          
          <v-list density="compact">
            <v-list-item>
              <template #prepend>
                <v-icon color="primary">mdi-calendar</v-icon>
              </template>
              <v-list-item-title>Membro desde</v-list-item-title>
              <v-list-item-subtitle>{{ formatDate(user?.created_at) }}</v-list-item-subtitle>
            </v-list-item>
            
            <v-list-item>
              <template #prepend>
                <v-icon color="success">mdi-check-circle</v-icon>
              </template>
              <v-list-item-title>Status da Conta</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip color="success" size="small">Ativa</v-chip>
              </v-list-item-subtitle>
            </v-list-item>
            
            <v-list-item>
              <template #prepend>
                <v-icon color="info">mdi-shield-check</v-icon>
              </template>
              <v-list-item-title>Tipo de Conta</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip :color="user?.is_superuser ? 'error' : 'primary'" size="small">
                  {{ user?.is_superuser ? 'Administrador' : 'Usuário' }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </BaseCard>
      </v-col>

      <!-- Profile Form -->
      <v-col cols="12" md="8">
        <BaseCard elevation="2">
          <template #title>
            <v-icon icon="mdi-form-textbox" class="mr-2" />
            Informações Pessoais
          </template>
          
          <v-form ref="profileForm" v-model="formValid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="profileData.full_name"
                  label="Nome Completo"
                  prepend-inner-icon="mdi-account"
                  variant="outlined"
                  :rules="nameRules"
                  required
                />
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="profileData.email"
                  label="Email"
                  prepend-inner-icon="mdi-email"
                  variant="outlined"
                  :rules="emailRules"
                  required
                  disabled
                  hint="Para alterar o email, entre em contato com o suporte"
                />
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="profileData.phone"
                  label="Telefone"
                  prepend-inner-icon="mdi-phone"
                  variant="outlined"
                  mask="(##) #####-####"
                />
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="profileData.company"
                  label="Empresa"
                  prepend-inner-icon="mdi-office-building"
                  variant="outlined"
                />
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="profileData.position"
                  label="Cargo"
                  prepend-inner-icon="mdi-badge-account"
                  variant="outlined"
                />
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="profileData.timezone"
                  :items="timezoneOptions"
                  label="Fuso Horário"
                  prepend-inner-icon="mdi-clock"
                  variant="outlined"
                />
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="profileData.bio"
                  label="Biografia"
                  prepend-inner-icon="mdi-text"
                  variant="outlined"
                  rows="3"
                  counter="500"
                  :rules="bioRules"
                />
              </v-col>
            </v-row>
          </v-form>
        </BaseCard>

        <!-- Security Section -->
        <BaseCard elevation="2" class="mt-6">
          <template #title>
            <v-icon icon="mdi-security" class="mr-2" />
            Segurança
          </template>
          
          <v-row>
            <v-col cols="12">
              <v-btn
                color="warning"
                variant="outlined"
                prepend-icon="mdi-lock-reset"
                @click="showPasswordDialog = true"
                block
              >
                Alterar Senha
              </v-btn>
            </v-col>
          </v-row>
        </BaseCard>

        <!-- Preferences -->
        <BaseCard elevation="2" class="mt-6">
          <template #title>
            <v-icon icon="mdi-cog" class="mr-2" />
            Preferências
          </template>
          
          <v-row>
            <v-col cols="12" md="6">
              <v-switch
                v-model="profileData.notifications_email"
                label="Receber notificações por email"
                color="primary"
                inset
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-switch
                v-model="profileData.notifications_app"
                label="Notificações no aplicativo"
                color="primary"
                inset
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-switch
                v-model="profileData.dark_mode"
                label="Modo escuro"
                color="primary"
                inset
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="profileData.language"
                :items="languageOptions"
                label="Idioma"
                prepend-inner-icon="mdi-translate"
                variant="outlined"
              />
            </v-col>
          </v-row>
        </BaseCard>
      </v-col>
    </v-row>

    <!-- Change Password Dialog -->
    <PasswordDialog
      v-model="showPasswordDialog"
      :loading="passwordLoading"
      @save="handlePasswordChange"
      @cancel="showPasswordDialog = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotifications } from '@/composables/useNotifications'
import { profileService } from '@/services/profile'

// Components
import PageHeader from '@/components/base/PageHeader.vue'
import BaseCard from '@/components/base/BaseCard.vue'
import PasswordDialog from '@/components/modals/PasswordDialog.vue'

// Stores & Composables
const authStore = useAuthStore()
const { showActionSuccess, showActionError } = useNotifications()

// Local state
const profileForm = ref(null)
const avatarInput = ref(null)
const formValid = ref(false)
const saving = ref(false)
const passwordLoading = ref(false)
const showPasswordDialog = ref(false)

// Profile data
const profileData = reactive({
  full_name: '',
  email: '',
  phone: '',
  company: '',
  position: '',
  bio: '',
  timezone: 'America/Sao_Paulo',
  language: 'pt-BR',
  notifications_email: true,
  notifications_app: true,
  dark_mode: false,
  avatar: null
})

const originalData = ref({})

// Options
const timezoneOptions = [
  { title: 'São Paulo (GMT-3)', value: 'America/Sao_Paulo' },
  { title: 'Brasília (GMT-3)', value: 'America/Brasilia' },
  { title: 'Manaus (GMT-4)', value: 'America/Manaus' }
]

const languageOptions = [
  { title: 'Português (Brasil)', value: 'pt-BR' },
  { title: 'English', value: 'en-US' },
  { title: 'Español', value: 'es-ES' }
]

// Validation rules
const nameRules = [
  v => !!v || 'Nome é obrigatório',
  v => (v && v.length >= 2) || 'Nome deve ter pelo menos 2 caracteres'
]

const emailRules = [
  v => !!v || 'Email é obrigatório',
  v => /.+@.+\..+/.test(v) || 'Email deve ser válido'
]

const bioRules = [
  v => !v || v.length <= 500 || 'Biografia deve ter no máximo 500 caracteres'
]

// Computed
const user = computed(() => authStore.user)

const hasChanges = computed(() => {
  return JSON.stringify(profileData) !== JSON.stringify(originalData.value)
})

// Methods
const loadProfile = async () => {
  try {
    const profile = await profileService.getProfile()
    Object.assign(profileData, profile)
    originalData.value = { ...profile }
  } catch (error) {
    console.error('Error loading profile:', error)
  }
}

const handleSave = async () => {
  if (!formValid.value) return
  
  try {
    saving.value = true
    
    const updated = await profileService.updateProfile(profileData)
    Object.assign(originalData.value, updated)
    
    // Update auth store
    await authStore.updateProfile(updated)
    
    showActionSuccess('update', 'Perfil')
    
  } catch (error) {
    showActionError('update', 'perfil', error.message)
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  Object.assign(profileData, originalData.value)
}

const selectAvatar = () => {
  avatarInput.value?.click()
}

const handleAvatarChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  try {
    const formData = new FormData()
    formData.append('avatar', file)
    
    const response = await profileService.uploadAvatar(formData)
    profileData.avatar = response.avatar_url
    
    showActionSuccess('update', 'Foto do perfil')
    
  } catch (error) {
    showActionError('update', 'foto do perfil', error.message)
  }
}

const handlePasswordChange = async (passwordData) => {
  try {
    passwordLoading.value = true
    
    await profileService.changePassword(passwordData)
    showActionSuccess('update', 'Senha')
    showPasswordDialog.value = false
    
  } catch (error) {
    showActionError('update', 'senha', error.message)
  } finally {
    passwordLoading.value = false
  }
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Intl.DateTimeFormat('pt-BR').format(new Date(date))
}

// Lifecycle
onMounted(() => {
  // Initialize with auth store data
  Object.assign(profileData, {
    full_name: user.value?.full_name || '',
    email: user.value?.email || '',
    ...user.value
  })
  originalData.value = { ...profileData }
  
  // Load full profile
  loadProfile()
})
</script>

<style scoped>
.profile-page {
  padding: 0;
}

.avatar-section {
  position: relative;
}

/* Responsividade */
@media (max-width: 768px) {
  .profile-page :deep(.header-actions) {
    flex-direction: column;
    gap: 8px;
  }
  
  .profile-page :deep(.header-actions .v-btn) {
    width: 100%;
  }
}
</style> 