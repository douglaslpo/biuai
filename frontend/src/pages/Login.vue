<template>
  <v-app>
    <!-- Background com gradiente -->
    <div class="biuai-auth-background">
      <div class="biuai-auth-overlay"></div>
    </div>

    <v-main>
      <v-container fluid class="fill-height pa-4">
        <v-row justify="center" align="center" class="fill-height">
          <v-col cols="12" sm="10" md="6" lg="5" xl="4">
            <!-- Card principal seguindo o protótipo -->
            <BaseCard 
              class="biuai-auth-card mx-auto"
              elevation="24"
              rounded="xl"
            >
              <!-- Header com logo -->
              <div class="text-center mb-8">
                <div class="biuai-logo-container mb-4">
                  <v-img
                    :src="logoUrl"
                    alt="BIUAI Logo"
                    max-width="64"
                    class="mx-auto"
                  />
                </div>
                <h1 class="biuai-text-h3 text-primary mb-2">
                  BIUAI
                </h1>
                <p class="text-body-1 text-medium-emphasis">
                  Business Intelligence Unity with AI
                </p>
              </div>

              <!-- Tabs de navegação -->
              <v-tabs
                v-model="tab"
                color="primary"
                align-tabs="center"
                class="mb-6"
                density="comfortable"
              >
                <v-tab 
                  value="login" 
                  class="text-none font-weight-medium"
                  rounded="lg"
                >
                  Entrar
                </v-tab>
                <v-tab 
                  value="register" 
                  class="text-none font-weight-medium"
                  rounded="lg"
                >
                  Criar Conta
                </v-tab>
              </v-tabs>

              <v-window v-model="tab">
                <!-- Tab de Login -->
                <v-window-item value="login">
                  <v-form
                    ref="loginForm"
                    v-model="loginValid"
                    @submit.prevent="handleLogin"
                  >
                    <div class="mb-6">
                      <!-- Email -->
                      <v-text-field
                        v-model="loginData.email"
                        type="email"
                        label="Email"
                        placeholder="seu@email.com"
                        prepend-inner-icon="mdi-email-outline"
                        :rules="emailRules"
                        required
                        class="mb-4"
                        variant="outlined"
                        density="comfortable"
                      />

                      <!-- Senha -->
                      <v-text-field
                        v-model="loginData.password"
                        :type="showPassword ? 'text' : 'password'"
                        label="Senha"
                        placeholder="Digite sua senha"
                        prepend-inner-icon="mdi-lock-outline"
                        :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                        @click:append-inner="showPassword = !showPassword"
                        :rules="passwordRules"
                        required
                        class="mb-4"
                        variant="outlined"
                        density="comfortable"
                      />

                      <!-- Lembrar de mim -->
                      <div class="d-flex align-center justify-space-between mb-4">
                        <v-checkbox
                          v-model="rememberMe"
                          label="Lembrar de mim"
                          color="primary"
                          density="comfortable"
                          hide-details
                        />
                        <v-btn
                          variant="text"
                          color="primary"
                          size="small"
                          class="text-none"
                          @click="showForgotPassword = true"
                        >
                          Esqueci minha senha
                        </v-btn>
                      </div>
                    </div>

                    <!-- Botão de login -->
                    <v-btn
                      type="submit"
                      color="primary"
                      variant="elevated"
                      size="large"
                      :loading="loading"
                      :disabled="!loginValid"
                      block
                      rounded="lg"
                      class="mb-4"
                    >
                      <v-icon start>mdi-login</v-icon>
                      Entrar
                    </v-btn>
                  </v-form>
                </v-window-item>

                <!-- Tab de Registro -->
                <v-window-item value="register">
                  <v-form
                    ref="registerForm"
                    v-model="registerValid"
                    @submit.prevent="handleRegister"
                  >
                    <div class="mb-6">
                      <!-- Nome completo -->
                      <v-text-field
                        v-model="registerData.full_name"
                        label="Nome Completo"
                        placeholder="Seu nome completo"
                        prepend-inner-icon="mdi-account-outline"
                        :rules="nameRules"
                        required
                        class="mb-4"
                        variant="outlined"
                        density="comfortable"
                      />

                      <!-- Email -->
                      <v-text-field
                        v-model="registerData.email"
                        type="email"
                        label="Email"
                        placeholder="seu@email.com"
                        prepend-inner-icon="mdi-email-outline"
                        :rules="emailRules"
                        required
                        class="mb-4"
                        variant="outlined"
                        density="comfortable"
                      />

                      <!-- Senha -->
                      <v-text-field
                        v-model="registerData.password"
                        :type="showRegisterPassword ? 'text' : 'password'"
                        label="Senha"
                        placeholder="Crie uma senha segura"
                        prepend-inner-icon="mdi-lock-outline"
                        :append-inner-icon="showRegisterPassword ? 'mdi-eye-off' : 'mdi-eye'"
                        @click:append-inner="showRegisterPassword = !showRegisterPassword"
                        hint="Mínimo 8 caracteres"
                        :rules="passwordRules"
                        required
                        class="mb-4"
                        variant="outlined"
                        density="comfortable"
                      />

                      <!-- Confirmar senha -->
                      <v-text-field
                        v-model="confirmPassword"
                        :type="showConfirmPassword ? 'text' : 'password'"
                        label="Confirmar Senha"
                        placeholder="Digite a senha novamente"
                        prepend-inner-icon="mdi-lock-check-outline"
                        :append-inner-icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
                        @click:append-inner="showConfirmPassword = !showConfirmPassword"
                        :rules="confirmPasswordRules"
                        required
                        class="mb-4"
                        variant="outlined"
                        density="comfortable"
                      />

                      <!-- Aceitar termos -->
                      <v-checkbox
                        v-model="acceptTerms"
                        color="primary"
                        density="comfortable"
                        hide-details
                        class="mb-4"
                      >
                        <template v-slot:label>
                          <div class="text-body-2">
                            Aceito os 
                            <a href="#" class="text-primary text-decoration-none" @click.prevent="showTerms = true">
                              termos de uso
                            </a>
                            e 
                            <a href="#" class="text-primary text-decoration-none" @click.prevent="showPrivacy = true">
                              política de privacidade
                            </a>
                          </div>
                        </template>
                      </v-checkbox>
                    </div>

                    <!-- Botão de registro -->
                    <v-btn
                      type="submit"
                      color="secondary"
                      variant="elevated"
                      size="large"
                      :loading="loading"
                      :disabled="!registerValid || !acceptTerms"
                      block
                      rounded="lg"
                      class="mb-4"
                    >
                      <v-icon start>mdi-account-plus</v-icon>
                      Criar Conta
                    </v-btn>
                  </v-form>
                </v-window-item>
              </v-window>

              <!-- Divider -->
              <v-divider class="my-6" />

              <!-- Acesso de demonstração -->
              <div class="text-center">
                <p class="text-caption text-medium-emphasis mb-4">
                  Acesso de demonstração
                </p>
                <v-btn
                  variant="outlined"
                  color="secondary"
                  size="default"
                  :loading="loading"
                  @click="demoLogin"
                  rounded="lg"
                >
                  <v-icon start>mdi-eye-outline</v-icon>
                  Testar Sistema
                </v-btn>
              </div>
            </BaseCard>

            <!-- Footer links -->
            <div class="text-center mt-6">
              <div class="d-flex justify-center align-center flex-wrap ga-4">
                <a href="#" class="text-caption text-medium-emphasis text-decoration-none">
                  Suporte
                </a>
                <span class="text-caption text-medium-emphasis">•</span>
                <a href="#" class="text-caption text-medium-emphasis text-decoration-none">
                  Documentação
                </a>
                <span class="text-caption text-medium-emphasis">•</span>
                <a href="#" class="text-caption text-medium-emphasis text-decoration-none">
                  Política de Privacidade
                </a>
              </div>
              <p class="text-caption text-medium-emphasis mt-2">
                © 2024 BIUAI. Todos os direitos reservados.
              </p>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <!-- Dialogs -->
    <v-dialog v-model="showForgotPassword" max-width="400">
      <BaseCard title="Recuperar Senha" icon="mdi-lock-reset">
        <p class="text-body-2 mb-4">
          Digite seu email para receber instruções de recuperação de senha.
        </p>
        <v-text-field
          v-model="forgotEmail"
          type="email"
          label="Email"
          placeholder="seu@email.com"
          prepend-inner-icon="mdi-email-outline"
          variant="outlined"
          required
          class="mb-4"
        />
        <template #actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="showForgotPassword = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="primary"
            :loading="loading"
            @click="handleForgotPassword"
          >
            Enviar
          </v-btn>
        </template>
      </BaseCard>
    </v-dialog>

    <!-- Snackbar para notificações -->
    <v-snackbar
      v-model="showNotification"
      :color="notificationType"
      :timeout="5000"
      location="top"
    >
      {{ notificationMessage }}
      <template #actions>
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="showNotification = false"
        />
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseCard from '@/components/base/BaseCard.vue'

// Stores e router
const authStore = useAuthStore()
const router = useRouter()

// Estados reativos
const tab = ref('login')
const loading = ref(false)
const loginValid = ref(false)
const registerValid = ref(false)
const rememberMe = ref(false)
const acceptTerms = ref(false)
const showPassword = ref(false)
const showRegisterPassword = ref(false)
const showConfirmPassword = ref(false)
const showForgotPassword = ref(false)
const showTerms = ref(false)
const showPrivacy = ref(false)
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref('info')

// Dados dos formulários
const loginData = ref({
  email: '',
  password: ''
})

const registerData = ref({
  full_name: '',
  email: '',
  password: ''
})

const confirmPassword = ref('')
const forgotEmail = ref('')

// URL do logo
const logoUrl = computed(() => '/images/biuai-logo.svg')

// Regras de validação
const emailRules = [
  v => !!v || 'Email é obrigatório',
  v => /.+@.+\..+/.test(v) || 'Email deve ser válido'
]

const passwordRules = [
  v => !!v || 'Senha é obrigatória',
  v => (v && v.length >= 8) || 'Senha deve ter pelo menos 8 caracteres'
]

const nameRules = [
  v => !!v || 'Nome é obrigatório',
  v => (v && v.length >= 2) || 'Nome deve ter pelo menos 2 caracteres'
]

const confirmPasswordRules = computed(() => [
  v => !!v || 'Confirmação de senha é obrigatória',
  v => v === registerData.value.password || 'Senhas não conferem'
])

// Métodos
const handleLogin = async () => {
  if (!loginValid.value) return
  
  loading.value = true
  
  try {
    const result = await authStore.login(loginData.value.email, loginData.value.password)
    
    if (result.success) {
      showNotificationMessage('Login realizado com sucesso!', 'success')
      router.push('/dashboard')
    } else {
      showNotificationMessage(result.error || 'Erro ao fazer login', 'error')
    }
  } catch (error) {
    showNotificationMessage(error.message || 'Erro ao fazer login', 'error')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerValid.value || !acceptTerms.value) return
  
  loading.value = true
  try {
    const result = await authStore.register(registerData.value)
    if (result.success) {
      showNotificationMessage('Conta criada com sucesso! Você já está logado.', 'success')
      router.push('/dashboard')
    } else {
      showNotificationMessage(result.error || 'Erro ao criar conta', 'error')
    }
    // Limpar dados do registro independente do resultado
    registerData.value = { full_name: '', email: '', password: '' }
    confirmPassword.value = ''
    acceptTerms.value = false
  } catch (error) {
    showNotificationMessage(error.message || 'Erro ao criar conta', 'error')
  } finally {
    loading.value = false
  }
}

const demoLogin = async () => {
  loading.value = true
  
  try {
    const result = await authStore.login('demo@biuai.com', 'demo123')
    
    if (result.success) {
      showNotificationMessage('Acesso demo ativado!', 'info')
      router.push('/dashboard')
    } else {
      showNotificationMessage(result.error || 'Erro no acesso demo', 'error')
    }
  } catch (error) {
    showNotificationMessage('Erro no acesso demo', 'error')
  } finally {
    loading.value = false
  }
}

const handleForgotPassword = async () => {
  if (!forgotEmail.value) return
  
  loading.value = true
  try {
    // Simular envio de email
    await new Promise(resolve => setTimeout(resolve, 2000))
    showNotificationMessage('Email de recuperação enviado!', 'success')
    showForgotPassword.value = false
    forgotEmail.value = ''
  } catch (error) {
    showNotificationMessage('Erro ao enviar email', 'error')
  } finally {
    loading.value = false
  }
}

const showNotificationMessage = (message, type = 'info') => {
  notificationMessage.value = message
  notificationType.value = type
  showNotification.value = true
}

// Lifecycle
onMounted(() => {
  // Verificar se já está logado
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
  }
})
</script>

<style lang="scss" scoped>
.biuai-auth-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, 
    rgb(var(--v-theme-primary)) 0%, 
    rgb(var(--v-theme-primary-darken-2)) 100%
  );
  z-index: -2;
}

.biuai-auth-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="1" fill="%23ffffff" opacity="0.1"/></svg>');
  background-size: 50px 50px;
  z-index: -1;
}

.biuai-auth-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-width: 480px;
  padding: 2rem;
}

.biuai-logo-container {
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80px;
    height: 80px;
    background: rgba(var(--v-theme-primary), 0.1);
    border-radius: 50%;
    z-index: -1;
  }
}

// Animações
.biuai-auth-card {
  animation: slideInUp 0.6s cubic-bezier(0.25, 0.8, 0.25, 1);
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// Responsividade
@media (max-width: 600px) {
  .biuai-auth-card {
    padding: 1.5rem;
    margin: 1rem;
  }
}
</style> 