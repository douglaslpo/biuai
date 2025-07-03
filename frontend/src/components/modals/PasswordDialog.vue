<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    persistent
    max-width="500px"
  >
    <v-card class="password-dialog">
      <v-card-title class="px-6 py-4 bg-primary text-white">
        <div class="d-flex align-center">
          <v-icon size="24" class="mr-3">mdi-lock-reset</v-icon>
          <span>Alterar Senha</span>
        </div>
      </v-card-title>

      <v-card-text class="px-6 py-4">
        <v-form ref="formRef" v-model="formValid" @submit.prevent="handleSave">
          <!-- Senha Atual -->
          <v-text-field
            v-model="form.senhaAtual"
            label="Senha Atual"
            :type="showCurrentPassword ? 'text' : 'password'"
            :rules="[rules.required]"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-lock"
            :append-inner-icon="showCurrentPassword ? 'mdi-eye' : 'mdi-eye-off'"
            @click:append-inner="showCurrentPassword = !showCurrentPassword"
            class="mb-3"
          />

          <!-- Nova Senha -->
          <v-text-field
            v-model="form.novaSenha"
            label="Nova Senha"
            :type="showNewPassword ? 'text' : 'password'"
            :rules="[rules.required, rules.minLength, rules.complexity]"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-lock-plus"
            :append-inner-icon="showNewPassword ? 'mdi-eye' : 'mdi-eye-off'"
            @click:append-inner="showNewPassword = !showNewPassword"
            class="mb-3"
          />

          <!-- Confirmar Nova Senha -->
          <v-text-field
            v-model="form.confirmarSenha"
            label="Confirmar Nova Senha"
            :type="showConfirmPassword ? 'text' : 'password'"
            :rules="[rules.required, rules.passwordMatch]"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-lock-check"
            :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
            @click:append-inner="showConfirmPassword = !showConfirmPassword"
            class="mb-3"
          />

          <!-- Strength Indicator -->
          <div v-if="form.novaSenha" class="password-strength mb-4">
            <div class="d-flex justify-space-between mb-2">
              <span class="text-body-2">Força da Senha</span>
              <span class="text-body-2 font-weight-bold" 
                    :class="strengthColor">
                {{ strengthText }}
              </span>
            </div>
            <v-progress-linear
              :model-value="strengthScore * 25"
              :color="strengthColor.replace('text-', '')"
              height="6"
              rounded
            />
            
            <!-- Requirements -->
            <div class="mt-3">
              <p class="text-caption text-medium-emphasis mb-2">Requisitos:</p>
              <div class="requirements">
                <div class="requirement" :class="{ 'met': hasMinLength }">
                  <v-icon size="16" :color="hasMinLength ? 'success' : 'grey'">
                    {{ hasMinLength ? 'mdi-check' : 'mdi-close' }}
                  </v-icon>
                  <span class="ml-2">Mínimo 8 caracteres</span>
                </div>
                
                <div class="requirement" :class="{ 'met': hasUppercase }">
                  <v-icon size="16" :color="hasUppercase ? 'success' : 'grey'">
                    {{ hasUppercase ? 'mdi-check' : 'mdi-close' }}
                  </v-icon>
                  <span class="ml-2">Letra maiúscula</span>
                </div>
                
                <div class="requirement" :class="{ 'met': hasLowercase }">
                  <v-icon size="16" :color="hasLowercase ? 'success' : 'grey'">
                    {{ hasLowercase ? 'mdi-check' : 'mdi-close' }}
                  </v-icon>
                  <span class="ml-2">Letra minúscula</span>
                </div>
                
                <div class="requirement" :class="{ 'met': hasNumber }">
                  <v-icon size="16" :color="hasNumber ? 'success' : 'grey'">
                    {{ hasNumber ? 'mdi-check' : 'mdi-close' }}
                  </v-icon>
                  <span class="ml-2">Número</span>
                </div>
                
                <div class="requirement" :class="{ 'met': hasSpecialChar }">
                  <v-icon size="16" :color="hasSpecialChar ? 'success' : 'grey'">
                    {{ hasSpecialChar ? 'mdi-check' : 'mdi-close' }}
                  </v-icon>
                  <span class="ml-2">Caractere especial</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Security Tips -->
          <v-alert
            type="info"
            variant="tonal"
            density="compact"
            icon="mdi-shield-check"
            class="mb-3"
          >
            <p class="text-body-2 mb-0">
              <strong>Dicas de Segurança:</strong>
            </p>
            <ul class="text-caption mt-1">
              <li>Use uma combinação única de caracteres</li>
              <li>Evite informações pessoais óbvias</li>
              <li>Considere usar um gerenciador de senhas</li>
            </ul>
          </v-alert>
        </v-form>
      </v-card-text>

      <v-card-actions class="px-6 py-4">
        <v-spacer />
        <v-btn
          variant="outlined"
          @click="handleCancel"
          :disabled="loading"
        >
          Cancelar
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          :loading="loading"
          @click="handleSave"
          :disabled="!formValid || strengthScore < 2"
        >
          Alterar Senha
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'save', 'cancel'])

// Refs
const formRef = ref(null)
const formValid = ref(false)
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// Form data
const form = ref({
  senhaAtual: '',
  novaSenha: '',
  confirmarSenha: ''
})

// Password strength checkers
const hasMinLength = computed(() => form.value.novaSenha.length >= 8)
const hasUppercase = computed(() => /[A-Z]/.test(form.value.novaSenha))
const hasLowercase = computed(() => /[a-z]/.test(form.value.novaSenha))
const hasNumber = computed(() => /\d/.test(form.value.novaSenha))
const hasSpecialChar = computed(() => /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(form.value.novaSenha))

const strengthScore = computed(() => {
  let score = 0
  if (hasMinLength.value) score++
  if (hasUppercase.value) score++
  if (hasLowercase.value) score++
  if (hasNumber.value) score++
  if (hasSpecialChar.value) score++
  return score
})

const strengthText = computed(() => {
  switch (strengthScore.value) {
    case 0:
    case 1: return 'Muito Fraca'
    case 2: return 'Fraca'
    case 3: return 'Moderada'
    case 4: return 'Forte'
    case 5: return 'Muito Forte'
    default: return 'Muito Fraca'
  }
})

const strengthColor = computed(() => {
  switch (strengthScore.value) {
    case 0:
    case 1: return 'text-error'
    case 2: return 'text-warning'
    case 3: return 'text-info'
    case 4: return 'text-success'
    case 5: return 'text-success'
    default: return 'text-error'
  }
})

// Validation rules
const rules = {
  required: value => !!value || 'Campo obrigatório',
  minLength: value => value.length >= 8 || 'Senha deve ter pelo menos 8 caracteres',
  complexity: value => {
    if (!value) return true
    const hasUpper = /[A-Z]/.test(value)
    const hasLower = /[a-z]/.test(value)
    const hasDigit = /\d/.test(value)
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(value)
    
    if (hasUpper && hasLower && hasDigit && hasSpecial) {
      return true
    }
    return 'Senha deve conter ao menos: 1 maiúscula, 1 minúscula, 1 número e 1 caractere especial'
  },
  passwordMatch: value => {
    if (!value) return true
    return value === form.value.novaSenha || 'Senhas não coincidem'
  }
}

// Methods
const resetForm = () => {
  form.value = {
    senhaAtual: '',
    novaSenha: '',
    confirmarSenha: ''
  }
  
  // Reset visibility states
  showCurrentPassword.value = false
  showNewPassword.value = false
  showConfirmPassword.value = false
}

const handleSave = async () => {
  if (!formRef.value) return
  
  const { valid } = await formRef.value.validate()
  if (!valid || strengthScore.value < 2) return

  const passwordData = {
    current_password: form.value.senhaAtual,
    new_password: form.value.novaSenha,
    confirm_password: form.value.confirmarSenha
  }

  emit('save', passwordData)
}

const handleCancel = () => {
  resetForm()
  emit('cancel')
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    resetForm()
  }
})
</script>

<style scoped>
.password-dialog {
  border-radius: 12px;
  overflow: hidden;
}

.password-strength {
  background: rgba(var(--v-theme-surface-variant), 0.1);
  border-radius: 8px;
  padding: 16px;
}

.requirements {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.requirement {
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.requirement.met {
  color: rgb(var(--v-theme-success));
}

/* Form styling */
.password-dialog :deep(.v-field__prepend-inner) {
  color: rgb(var(--v-theme-primary));
}

.password-dialog :deep(.v-text-field input) {
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .password-dialog {
    margin: 16px;
    max-width: calc(100vw - 32px);
  }
  
  .password-dialog :deep(.v-card-title) {
    font-size: 1.1rem;
  }
  
  .requirements {
    font-size: 0.7rem;
  }
}
</style> 