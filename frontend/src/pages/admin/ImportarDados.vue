<template>
  <v-container fluid class="pa-6">
    <div class="d-flex align-center mb-6">
      <v-icon color="primary" size="32" class="mr-3">mdi-database-import</v-icon>
      <div>
        <h1 class="text-h4 font-weight-bold">Importar Dados</h1>
        <p class="text-subtitle-1 text-medium-emphasis mb-0">
          Importe dados financeiros de diferentes fontes
        </p>
      </div>
    </div>

    <v-row>
      <!-- Upload de Arquivos -->
      <v-col cols="12" md="8">
        <BaseCard title="Upload de Arquivo" icon="mdi-file-upload">
          <v-file-input
            v-model="selectedFile"
            label="Selecione um arquivo"
            prepend-icon="mdi-paperclip"
            accept=".csv,.xlsx,.xls,.json"
            show-size
            clearable
            :loading="uploading"
            @change="onFileSelect"
          />
          
          <v-alert
            v-if="fileInfo"
            type="info"
            variant="tonal"
            class="mb-4"
          >
            <div class="d-flex align-center">
              <v-icon class="mr-2">mdi-information</v-icon>
              <div>
                <strong>{{ fileInfo.name }}</strong><br>
                <small>{{ fileInfo.size }} | {{ fileInfo.type }}</small>
              </div>
            </div>
          </v-alert>

          <!-- Botões de Ação -->
          <div class="d-flex gap-3">
            <v-btn
              color="primary"
              variant="elevated"
              :loading="uploading"
              :disabled="!selectedFile"
              @click="processFile"
            >
              <v-icon start>mdi-file-check</v-icon>
              Processar Arquivo
            </v-btn>
            
            <v-btn
              color="secondary"
              variant="outlined"
              :disabled="!selectedFile || uploading"
              @click="importData"
            >
              <v-icon start>mdi-database-import</v-icon>
              Importar Dados
            </v-btn>
          </div>
        </BaseCard>
      </v-col>

      <!-- Histórico e Status -->
      <v-col cols="12" md="4">
        <BaseCard title="Status da Importação" icon="mdi-chart-line">
          <v-list density="compact">
            <v-list-item
              prepend-icon="mdi-database"
              title="Total de Registros"
              subtitle="0"
            />
            <v-list-item
              prepend-icon="mdi-check-circle"
              title="Registros Válidos"
              subtitle="0"
            />
          </v-list>
        </BaseCard>
      </v-col>
    </v-row>

    <!-- Snackbar para notificações -->
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
import { ref, computed } from 'vue'
import BaseCard from '@/components/base/BaseCard.vue'

// Estado reativo
const selectedFile = ref(null)
const uploading = ref(false)
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref('info')

// Informações do arquivo
const fileInfo = computed(() => {
  if (!selectedFile.value) return null
  
  return {
    name: selectedFile.value.name,
    size: formatFileSize(selectedFile.value.size),
    type: selectedFile.value.type || 'Desconhecido'
  }
})

// Métodos
const onFileSelect = (file) => {
  if (file) {
    showNotificationMessage('Arquivo selecionado. Clique em "Processar Arquivo" para visualizar os dados.', 'info')
  }
}

const processFile = async () => {
  if (!selectedFile.value) return
  
  uploading.value = true
  
  try {
    // Simular processamento
    await new Promise(resolve => setTimeout(resolve, 2000))
    showNotificationMessage('Arquivo processado com sucesso!', 'success')
  } catch (error) {
    showNotificationMessage('Erro ao processar arquivo: ' + error.message, 'error')
  } finally {
    uploading.value = false
  }
}

const importData = async () => {
  if (!selectedFile.value) return
  
  uploading.value = true
  
  try {
    // Simular importação
    await new Promise(resolve => setTimeout(resolve, 3000))
    showNotificationMessage('Dados importados com sucesso!', 'success')
    
    // Limpar formulário
    selectedFile.value = null
    
  } catch (error) {
    showNotificationMessage('Erro na importação: ' + error.message, 'error')
  } finally {
    uploading.value = false
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const showNotificationMessage = (message, type = 'info') => {
  notificationMessage.value = message
  notificationType.value = type
  showNotification.value = true
}
</script>

<style lang="scss" scoped>
.v-file-input {
  :deep(.v-field__input) {
    padding-top: 8px;
  }
}
</style>
