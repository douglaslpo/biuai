import { api } from '@/boot/axios'

export const profileService = {
  // Buscar dados do perfil do usuário
  async getProfile() {
    const response = await api.get('/api/v1/usuarios/profile')
    return response.data
  },

  // Atualizar dados do perfil
  async updateProfile(profileData) {
    const response = await api.put('/api/v1/usuarios/profile', profileData)
    return response.data
  },

  // Alterar senha do usuário
  async changePassword(passwordData) {
    const response = await api.put('/api/v1/usuarios/change-password', passwordData)
    return response.data
  },

  // Upload de avatar
  async uploadAvatar(file) {
    const formData = new FormData()
    formData.append('avatar', file)
    
    const response = await api.post('/api/v1/usuarios/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // Buscar preferências do usuário
  async getPreferences() {
    const response = await api.get('/api/v1/usuarios/preferences')
    return response.data
  },

  // Atualizar preferências do usuário
  async updatePreferences(preferences) {
    const response = await api.put('/api/v1/usuarios/preferences', preferences)
    return response.data
  },

  // Buscar estatísticas do usuário
  async getStats() {
    const response = await api.get('/api/v1/usuarios/stats')
    return response.data
  },

  // Desativar conta
  async deactivateAccount() {
    const response = await api.post('/api/v1/usuarios/deactivate')
    return response.data
  },

  // Solicitar exclusão de dados (LGPD)
  async requestDataDeletion() {
    const response = await api.post('/api/v1/usuarios/request-deletion')
    return response.data
  },

  // Baixar dados do usuário (LGPD)
  async downloadUserData() {
    const response = await api.get('/api/v1/usuarios/download-data', {
      responseType: 'blob'
    })
    return response.data
  }
}

export default profileService 