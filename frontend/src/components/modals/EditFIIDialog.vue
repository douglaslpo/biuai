<template>
  <v-dialog v-model="dialog" max-width="600px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Editar FII</span>
      </v-card-title>

      <v-card-text>
        <v-form ref="form" v-model="valid" @submit.prevent="handleSubmit">
          <v-container>
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="fiiData.codigo"
                  :rules="[v => !!v || 'Código é obrigatório', v => /^[A-Z0-9]{4,6}11$/.test(v) || 'Código inválido']"
                  label="Código do FII"
                  required
                  hint="Ex: HGLG11"
                  persistent-hint
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="fiiData.nome"
                  :rules="[v => !!v || 'Nome é obrigatório']"
                  label="Nome do FII"
                  required
                ></v-text-field>
              </v-col>

              <v-col cols="12" sm="6">
                <v-select
                  v-model="fiiData.segmento"
                  :items="segmentos"
                  label="Segmento"
                  required
                  :rules="[v => !!v || 'Segmento é obrigatório']"
                ></v-select>
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="fiiData.preco_atual"
                  type="number"
                  label="Preço Atual"
                  prefix="R$"
                  :rules="[
                    v => !!v || 'Preço é obrigatório',
                    v => v > 0 || 'Preço deve ser maior que zero'
                  ]"
                  required
                ></v-text-field>
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="fiiData.dividend_yield"
                  type="number"
                  label="Dividend Yield"
                  suffix="%"
                  :rules="[
                    v => v >= 0 || 'DY não pode ser negativo'
                  ]"
                ></v-text-field>
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="fiiData.patrimonio_liquido"
                  type="number"
                  label="Patrimônio Líquido"
                  prefix="R$"
                  :rules="[v => v > 0 || 'Patrimônio deve ser maior que zero']"
                ></v-text-field>
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="fiiData.valor_patrimonial"
                  type="number"
                  label="Valor Patrimonial"
                  prefix="R$"
                  :rules="[v => v > 0 || 'Valor patrimonial deve ser maior que zero']"
                ></v-text-field>
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="fiiData.liquidez_diaria"
                  type="number"
                  label="Liquidez Diária"
                  prefix="R$"
                  :rules="[v => v >= 0 || 'Liquidez não pode ser negativa']"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="blue-darken-1"
          variant="text"
          @click="dialog = false"
        >
          Cancelar
        </v-btn>
        <v-btn
          color="blue-darken-1"
          variant="text"
          @click="handleSubmit"
          :loading="loading"
          :disabled="!valid"
        >
          Salvar
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { useNotifications } from '@/composables/useNotifications'
import { useMyFIIs } from '@/modules/myfiis/composables/useMyFIIs'
import { reactive, ref, watch } from 'vue'

const props = defineProps({
  fii: {
    type: Object,
    required: true
  },
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const dialog = ref(false)
const valid = ref(false)
const loading = ref(false)
const form = ref(null)

const { updateFII } = useMyFIIs()
const { showSuccess, showError } = useNotifications()

const segmentos = [
  'Logística',
  'Shoppings',
  'Lajes Corporativas',
  'Residencial',
  'Híbrido',
  'Papel',
  'Outros'
]

const fiiData = reactive({
  codigo: '',
  nome: '',
  segmento: '',
  preco_atual: null,
  dividend_yield: null,
  patrimonio_liquido: null,
  valor_patrimonial: null,
  liquidez_diaria: null
})

watch(() => props.modelValue, (newValue) => {
  dialog.value = newValue
})

watch(dialog, (newValue) => {
  emit('update:modelValue', newValue)
  if (newValue) {
    Object.assign(fiiData, props.fii)
  }
})

const handleSubmit = async () => {
  if (!form.value.validate()) return

  try {
    loading.value = true
    await updateFII(props.fii.id, fiiData)
    showSuccess('FII atualizado com sucesso!')
    dialog.value = false
  } catch (error) {
    showError('Erro ao atualizar FII: ' + error.message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.v-card-title {
  background-color: var(--v-primary-base);
  color: white;
  padding: 16px;
}

.v-form {
  padding-top: 16px;
}
</style> 