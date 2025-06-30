<template>
  <v-container fluid class="pa-6">
    <div class="d-flex align-center mb-6">
      <v-icon color="primary" size="32" class="mr-3">mdi-backup-restore</v-icon>
      <div>
        <h1 class="text-h4 font-weight-bold">Backup e Restore</h1>
        <p class="text-subtitle-1 text-medium-emphasis mb-0">
          Gerencie backups do banco de dados e arquivos do sistema
        </p>
      </div>
    </div>

    <v-row>
      <!-- Criar Backup -->
      <v-col cols="12" md="6">
        <BaseCard title="Criar Backup" icon="mdi-content-save">
          <v-form @submit.prevent="createBackup">
            <v-text-field
              v-model="backupForm.name"
              label="Nome do Backup"
              placeholder="backup_2024_06_29"
              prepend-inner-icon="mdi-tag"
              variant="outlined"
              :rules="[v => !!v || 'Nome é obrigatório']"
              class="mb-4"
            />
            
            <v-textarea
              v-model="backupForm.description"
              label="Descrição (opcional)"
              placeholder="Backup antes da atualização..."
              prepend-inner-icon="mdi-text"
              variant="outlined"
              rows="3"
              class="mb-4"
            />
            
            <v-select
              v-model="backupForm.type"
              label="Tipo de Backup"
              :items="backupTypes"
              variant="outlined"
              prepend-inner-icon="mdi-database"
              class="mb-4"
            />
            
            <v-checkbox
              v-model="backupForm.includeFiles"
              label="Incluir arquivos de upload"
              color="primary"
              class="mb-4"
            />
            
            <v-btn
              type="submit"
              color="primary"
              variant="elevated"
              :loading="creating"
              block
            >
              <v-icon start>mdi-backup-restore</v-icon>
              Criar Backup
            </v-btn>
          </v-form>
        </BaseCard>
      </v-col>

      <!-- Upload de Backup -->
      <v-col cols="12" md="6">
        <BaseCard title="Restaurar Backup" icon="mdi-restore">
          <v-file-input
            v-model="restoreFile"
            label="Selecione um arquivo de backup"
            prepend-icon="mdi-file-upload"
            accept=".sql,.tar.gz,.zip"
            show-size
            clearable
            class="mb-4"
          />
          
          <v-alert
            type="warning"
            variant="tonal"
            class="mb-4"
          >
            <v-icon class="mr-2">mdi-alert</v-icon>
            <strong>Atenção:</strong> A restauração irá substituir todos os dados atuais.
            Recomenda-se criar um backup antes de prosseguir.
          </v-alert>
          
          <v-btn
            color="warning"
            variant="elevated"
            :loading="restoring"
            :disabled="!restoreFile"
            @click="showRestoreDialog = true"
            block
          >
            <v-icon start>mdi-restore</v-icon>
            Restaurar Backup
          </v-btn>
        </BaseCard>

        <!-- Configurações de Backup -->
        <BaseCard title="Configurações Automáticas" icon="mdi-cog" class="mt-4">
          <v-switch
            v-model="autoBackup.enabled"
            label="Backup Automático"
            color="primary"
            inset
            class="mb-3"
          />
          
          <v-select
            v-model="autoBackup.frequency"
            label="Frequência"
            :items="frequencyOptions"
            variant="outlined"
            :disabled="!autoBackup.enabled"
            class="mb-3"
          />
          
          <v-text-field
            v-model="autoBackup.retention"
            label="Manter por (dias)"
            type="number"
            variant="outlined"
            :disabled="!autoBackup.enabled"
            class="mb-3"
          />
          
          <v-btn
            color="secondary"
            variant="outlined"
            :disabled="!autoBackup.enabled"
            @click="saveAutoBackupConfig"
            block
          >
            <v-icon start>mdi-content-save</v-icon>
            Salvar Configurações
          </v-btn>
        </BaseCard>
      </v-col>

      <!-- Lista de Backups -->
      <v-col cols="12">
        <BaseCard title="Backups Disponíveis" icon="mdi-folder-multiple">
          <v-data-table
            :headers="backupHeaders"
            :items="backups"
            :loading="loadingBackups"
            item-value="id"
            class="elevation-1"
          >
            <template v-slot:item.size="{ item }">
              {{ formatFileSize(item.size) }}
            </template>
            
            <template v-slot:item.type="{ item }">
              <v-chip
                :color="getTypeColor(item.type)"
                size="small"
                variant="tonal"
              >
                {{ item.type }}
              </v-chip>
            </template>
            
            <template v-slot:item.status="{ item }">
              <v-chip
                :color="item.status === 'completed' ? 'success' : item.status === 'failed' ? 'error' : 'warning'"
                size="small"
                variant="tonal"
              >
                {{ getStatusText(item.status) }}
              </v-chip>
            </template>
            
            <template v-slot:item.actions="{ item }">
              <div class="d-flex gap-2">
                <v-btn
                  color="primary"
                  variant="text"
                  size="small"
                  :disabled="item.status !== 'completed'"
                  @click="downloadBackup(item)"
                >
                  <v-icon>mdi-download</v-icon>
                </v-btn>
                
                <v-btn
                  color="warning"
                  variant="text"
                  size="small"
                  :disabled="item.status !== 'completed'"
                  @click="restoreBackup(item)"
                >
                  <v-icon>mdi-restore</v-icon>
                </v-btn>
                
                <v-btn
                  color="error"
                  variant="text"
                  size="small"
                  @click="deleteBackup(item)"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </div>
            </template>
          </v-data-table>
        </BaseCard>
      </v-col>
    </v-row>

    <!-- Dialog de Confirmação de Restore -->
    <v-dialog v-model="showRestoreDialog" max-width="500">
      <BaseCard title="Confirmar Restauração" icon="mdi-alert">
        <p class="mb-4">
          Tem certeza que deseja restaurar este backup? 
          <strong>Esta ação não pode ser desfeita</strong> e todos os dados atuais serão perdidos.
        </p>
        
        <v-text-field
          v-model="confirmText"
          label='Digite "CONFIRMAR" para prosseguir'
          variant="outlined"
          class="mb-4"
        />
        
        <template #actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="showRestoreDialog = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="warning"
            :disabled="confirmText !== 'CONFIRMAR'"
            :loading="restoring"
            @click="confirmRestore"
          >
            Restaurar
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
import { ref, reactive, onMounted } from 'vue'
import BaseCard from '@/components/base/BaseCard.vue'
import { api } from '@/boot/axios'

// Estado reativo
const creating = ref(false)
const restoring = ref(false)
const loadingBackups = ref(false)
const restoreFile = ref(null)
const showRestoreDialog = ref(false)
const confirmText = ref('')
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref('info')

// Formulário de backup
const backupForm = reactive({
  name: '',
  description: '',
  type: 'full',
  includeFiles: true
})

// Configurações de backup automático
const autoBackup = reactive({
  enabled: false,
  frequency: 'daily',
  retention: 30
})

// Opções
const backupTypes = [
  { title: 'Completo (Dados + Estrutura)', value: 'full' },
  { title: 'Apenas Dados', value: 'data' },
  { title: 'Apenas Estrutura', value: 'structure' }
]

const frequencyOptions = [
  { title: 'Diário', value: 'daily' },
  { title: 'Semanal', value: 'weekly' },
  { title: 'Mensal', value: 'monthly' }
]

// Headers da tabela
const backupHeaders = [
  { title: 'Nome', key: 'name', sortable: true },
  { title: 'Descrição', key: 'description', sortable: false },
  { title: 'Tipo', key: 'type', sortable: true },
  { title: 'Tamanho', key: 'size', sortable: true },
  { title: 'Data', key: 'created_at', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false }
]

// Lista de backups
const backups = ref([
  {
    id: 1,
    name: 'backup_2024_06_29',
    description: 'Backup automático diário',
    type: 'full',
    size: 15728640, // 15MB
    created_at: '2024-06-29 02:00:00',
    status: 'completed'
  },
  {
    id: 2,
    name: 'backup_pre_update',
    description: 'Backup antes da atualização v2.0',
    type: 'full',
    size: 14680064, // 14MB
    created_at: '2024-06-28 14:30:00',
    status: 'completed'
  },
  {
    id: 3,
    name: 'backup_2024_06_27',
    description: 'Backup automático diário',
    type: 'data',
    size: 8388608, // 8MB
    created_at: '2024-06-27 02:00:00',
    status: 'completed'
  }
])

// Métodos
const createBackup = async () => {
  if (!backupForm.name) return
  
  creating.value = true
  
  try {
    const response = await api.post('/admin/backup/create', backupForm)
    
    // Adicionar o novo backup à lista
    backups.value.unshift({
      ...response.data,
      created_at: new Date().toLocaleString('pt-BR')
    })
    
    // Limpar formulário
    Object.keys(backupForm).forEach(key => {
      if (typeof backupForm[key] === 'string') backupForm[key] = ''
      if (typeof backupForm[key] === 'boolean') backupForm[key] = false
    })
    backupForm.type = 'full'
    
    showNotificationMessage('Backup criado com sucesso!', 'success')
  } catch (error) {
    showNotificationMessage('Erro ao criar backup: ' + error.message, 'error')
  } finally {
    creating.value = false
  }
}

const confirmRestore = async () => {
  if (confirmText.value !== 'CONFIRMAR') return
  
  restoring.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', restoreFile.value)
    
    await api.post('/admin/backup/restore', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    showNotificationMessage('Backup restaurado com sucesso!', 'success')
    showRestoreDialog.value = false
    confirmText.value = ''
    restoreFile.value = null
  } catch (error) {
    showNotificationMessage('Erro ao restaurar backup: ' + error.message, 'error')
  } finally {
    restoring.value = false
  }
}

const downloadBackup = (backup) => {
  const link = document.createElement('a')
  link.href = `/api/v1/admin/backup/download/${backup.id}`
  link.download = `${backup.name}.sql`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  showNotificationMessage('Download iniciado!', 'info')
}

const restoreBackup = (backup) => {
  // Simular seleção do backup para restore
  showRestoreDialog.value = true
  confirmText.value = ''
}

const deleteBackup = async (backup) => {
  if (!confirm(`Tem certeza que deseja excluir o backup "${backup.name}"?`)) return
  
  try {
    await api.delete(`/admin/backup/${backup.id}`)
    
    const index = backups.value.findIndex(b => b.id === backup.id)
    if (index > -1) {
      backups.value.splice(index, 1)
    }
    
    showNotificationMessage('Backup excluído com sucesso!', 'success')
  } catch (error) {
    showNotificationMessage('Erro ao excluir backup: ' + error.message, 'error')
  }
}

const saveAutoBackupConfig = async () => {
  try {
    await api.put('/admin/backup/auto-config', autoBackup)
    showNotificationMessage('Configurações salvas com sucesso!', 'success')
  } catch (error) {
    showNotificationMessage('Erro ao salvar configurações: ' + error.message, 'error')
  }
}

const loadBackups = async () => {
  loadingBackups.value = true
  
  try {
    const response = await api.get('/admin/backup')
    backups.value = response.data
  } catch (error) {
    showNotificationMessage('Erro ao carregar backups: ' + error.message, 'error')
  } finally {
    loadingBackups.value = false
  }
}

const loadAutoBackupConfig = async () => {
  try {
    const response = await api.get('/admin/backup/auto-config')
    Object.assign(autoBackup, response.data)
  } catch (error) {
    console.error('Erro ao carregar configurações de backup automático:', error)
  }
}

// Utilitários
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getTypeColor = (type) => {
  const colors = {
    full: 'primary',
    data: 'success',
    structure: 'info'
  }
  return colors[type] || 'default'
}

const getStatusText = (status) => {
  const texts = {
    completed: 'Concluído',
    failed: 'Falhou',
    running: 'Executando'
  }
  return texts[status] || status
}

const showNotificationMessage = (message, type = 'info') => {
  notificationMessage.value = message
  notificationType.value = type
  showNotification.value = true
}

// Lifecycle
onMounted(() => {
  loadBackups()
  loadAutoBackupConfig()
})
</script>

<style lang="scss" scoped>
.v-data-table {
  border-radius: 8px;
  overflow: hidden;
}
</style> 