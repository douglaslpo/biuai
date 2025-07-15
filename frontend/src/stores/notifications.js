import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useNotificationStore = defineStore('notifications', () => {
  // State
  const notifications = ref([])
  const snackbar = ref({
    show: false,
    message: '',
    color: 'info',
    timeout: 4000
  })

  // Actions
  const showSuccess = (message, timeout = 4000) => {
    console.log('Success notification:', message)
    snackbar.value = {
      show: true,
      message,
      color: 'success',
      timeout
    }
    addNotification(message, 'success')
  }

  const showError = (message, timeout = 6000) => {
    console.error('Error notification:', message)
    snackbar.value = {
      show: true,
      message,
      color: 'error',
      timeout
    }
    addNotification(message, 'error')
  }

  const showWarning = (message, timeout = 5000) => {
    console.warn('Warning notification:', message)
    snackbar.value = {
      show: true,
      message,
      color: 'warning',
      timeout
    }
    addNotification(message, 'warning')
  }

  const showInfo = (message, timeout = 4000) => {
    console.info('Info notification:', message)
    snackbar.value = {
      show: true,
      message,
      color: 'info',
      timeout
    }
    addNotification(message, 'info')
  }

  const hideSnackbar = () => {
    snackbar.value.show = false
  }

  const addNotification = (message, type = 'info') => {
    const notification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date(),
      read: false
    }
    
    notifications.value.unshift(notification)
    
    // Manter apenas as últimas 50 notificações
    if (notifications.value.length > 50) {
      notifications.value = notifications.value.slice(0, 50)
    }
  }

  const markAsRead = (notificationId) => {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.read = true
    }
  }

  const removeNotification = (notificationId) => {
    const index = notifications.value.findIndex(n => n.id === notificationId)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearAll = () => {
    notifications.value = []
  }

  // Getters
  const unreadCount = computed(() => {
    return notifications.value.filter(n => !n.read).length
  })

  const recentNotifications = computed(() => {
    return notifications.value.slice(0, 10)
  })

  return {
    // State
    notifications,
    snackbar,
    
    // Actions
    showSuccess,
    showError,
    showWarning,
    showInfo,
    hideSnackbar,
    addNotification,
    markAsRead,
    removeNotification,
    clearAll,
    
    // Getters
    unreadCount,
    recentNotifications
  }
}) 