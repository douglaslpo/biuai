<template>
  <q-card-section>
    <div class="text-h6 text-center q-mb-md">Sistema Financeiro</div>
    
    <q-form @submit.prevent="onSubmit" class="q-gutter-md">
      <q-input
        v-model="form.full_name"
        label="Nome"
        :rules="[val => !!val || 'Campo obrigatório']"
        :disable="authStore.loading"
        :error="!!authStore.error"
      />

      <q-input
        v-model="form.email"
        type="email"
        label="E-mail"
        :rules="[
          val => !!val || 'Campo obrigatório',
          val => /^[^@]+@[^@]+\.[^@]+$/.test(val) || 'E-mail inválido'
        ]"
        :disable="authStore.loading"
        :error="!!authStore.error"
      />

      <q-input
        v-model="form.password"
        type="password"
        label="Senha"
        :rules="[
          val => !!val || 'Campo obrigatório',
          val => val.length >= 6 || 'A senha deve ter no mínimo 6 caracteres'
        ]"
        :disable="authStore.loading"
        :error="!!authStore.error"
      />

      <q-input
        v-model="form.confirmPassword"
        type="password"
        label="Confirmar Senha"
        :rules="[
          val => !!val || 'Campo obrigatório',
          val => val === form.password || 'As senhas não conferem'
        ]"
        :disable="authStore.loading"
        :error="!!authStore.error"
      />

      <div v-if="authStore.error" class="text-negative text-center q-mb-md">
        {{ authStore.error }}
      </div>

      <div class="row justify-between items-center">
        <q-btn
          flat
          color="primary"
          label="Já tenho conta"
          to="/login"
          :disable="authStore.loading"
        />

        <q-btn
          type="submit"
          color="primary"
          label="Criar conta"
          :loading="authStore.loading"
        />
      </div>
    </q-form>
  </q-card-section>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'RegistroPage',

  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const form = ref({
      full_name: '',
      email: '',
      password: '',
      confirmPassword: ''
    })

    const onSubmit = async () => {
      try {
        const { confirmPassword, ...userData } = form.value
        await authStore.register(userData)
        
        $q.notify({
          type: 'positive',
          message: 'Conta criada com sucesso!'
        })
        
        router.push('/dashboard')
      } catch (error) {
        console.error('Erro no registro:', error)
        $q.notify({
          type: 'negative',
          message: authStore.error || 'Erro ao criar conta'
        })
      }
    }

    return {
      form,
      authStore,
      onSubmit
    }
  }
}
</script>

<style lang="scss" scoped>
.q-form {
  max-width: 400px;
  margin: 0 auto;
}

.q-card-section {
  padding: 2rem;
}
</style> 