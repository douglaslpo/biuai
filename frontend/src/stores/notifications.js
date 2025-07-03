import { defineStore } from 'pinia'

export const useNotificationStore = defineStore('notifications', {
  state: () => ({
    notifications: [],
    toasts: [],
    snackbars: [],
    preferences: {
      enabled: true,
      position: 'top-right',
      duration: 5000,
      maxVisible: 5,
      showIcons: true,
      playSound: false,
      animations: true
    }
  }),

  getters: {
    activeNotifications: (state) => {
      return state.notifications.filter(n => !n.dismissed && !n.read)
    },

    unreadCount: (state) => {
      return state.notifications.filter(n => !n.read).length
    },

    priorityNotifications: (state) => {
      return state.notifications
        .filter(n => n.priority === 'high' && !n.dismissed)
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    },

    visibleToasts: (state) => {
      return state.toasts.slice(0, state.preferences.maxVisible)
    }
  },

  actions: {
    // Core notification methods
    createNotification(notification) {
      const id = Date.now() + Math.random()
      const newNotification = {
        id,
        title: notification.title || 'Notificação',
        message: notification.message || '',
        type: notification.type || 'info', // success, error, warning, info
        priority: notification.priority || 'medium', // low, medium, high, urgent
        category: notification.category || 'general',
        icon: notification.icon || this.getDefaultIcon(notification.type),
        actions: notification.actions || [],
        persistent: notification.persistent || false,
        dismissible: notification.dismissible !== false,
        read: false,
        dismissed: false,
        created_at: new Date(),
        expires_at: notification.expires_at || null,
        data: notification.data || {}
      }

      this.notifications.unshift(newNotification)
      
      // Auto-expire if needed
      if (newNotification.expires_at) {
        setTimeout(() => {
          this.dismissNotification(id)
        }, new Date(newNotification.expires_at) - new Date())
      }

      // Play sound if enabled
      if (this.preferences.playSound && newNotification.priority === 'high') {
        this.playNotificationSound(newNotification.type)
      }

      return newNotification
    },

    // Toast notifications (temporary messages)
    showToast(toast) {
      const id = Date.now() + Math.random()
      const newToast = {
        id,
        message: toast.message || '',
        type: toast.type || 'info',
        duration: toast.duration || this.preferences.duration,
        icon: toast.icon || this.getDefaultIcon(toast.type),
        actions: toast.actions || [],
        persistent: toast.persistent || false,
        position: toast.position || this.preferences.position,
        created_at: new Date()
      }

      this.toasts.unshift(newToast)

      // Auto-remove toast
      if (!newToast.persistent) {
        setTimeout(() => {
          this.removeToast(id)
        }, newToast.duration)
      }

      return newToast
    },

    // Convenience methods for different types
    showSuccess(message, options = {}) {
      return this.showToast({
        message,
        type: 'success',
        icon: 'mdi-check-circle',
        ...options
      })
    },

    showError(message, options = {}) {
      return this.showToast({
        message,
        type: 'error',
        icon: 'mdi-alert-circle',
        duration: 8000, // Longer for errors
        ...options
      })
    },

    showWarning(message, options = {}) {
      return this.showToast({
        message,
        type: 'warning',
        icon: 'mdi-alert',
        ...options
      })
    },

    showInfo(message, options = {}) {
      return this.showToast({
        message,
        type: 'info',
        icon: 'mdi-information',
        ...options
      })
    },

    // Snackbar notifications (bottom notifications)
    showSnackbar(snackbar) {
      const id = Date.now() + Math.random()
      const newSnackbar = {
        id,
        message: snackbar.message || '',
        type: snackbar.type || 'info',
        duration: snackbar.duration || 4000,
        action: snackbar.action || null,
        actionText: snackbar.actionText || 'Desfazer',
        color: snackbar.color || this.getTypeColor(snackbar.type),
        created_at: new Date()
      }

      this.snackbars.push(newSnackbar)

      // Auto-remove snackbar
      setTimeout(() => {
        this.removeSnackbar(id)
      }, newSnackbar.duration)

      return newSnackbar
    },

    // System-level notifications
    notifyDataUpdate(message) {
      this.createNotification({
        title: 'Dados Atualizados',
        message,
        type: 'success',
        category: 'system',
        priority: 'low',
        expires_at: new Date(Date.now() + 30000) // 30 seconds
      })
    },

    notifyError(error, context = '') {
      this.createNotification({
        title: 'Erro no Sistema',
        message: `${context ? context + ': ' : ''}${error.message || error}`,
        type: 'error',
        category: 'system',
        priority: 'high',
        persistent: true,
        actions: [
          {
            text: 'Reportar',
            action: () => this.reportError(error, context)
          }
        ]
      })
    },

    notifyOffline() {
      this.createNotification({
        title: 'Conexão Perdida',
        message: 'Você está offline. Algumas funcionalidades podem não estar disponíveis.',
        type: 'warning',
        category: 'connectivity',
        priority: 'high',
        persistent: true,
        icon: 'mdi-wifi-off'
      })
    },

    notifyOnline() {
      this.createNotification({
        title: 'Conexão Restaurada',
        message: 'Você está online novamente.',
        type: 'success',
        category: 'connectivity',
        priority: 'medium',
        expires_at: new Date(Date.now() + 5000) // 5 seconds
      })
    },

    // Financial notifications
    notifyGoalReached(goal) {
      this.createNotification({
        title: '🎯 Meta Alcançada!',
        message: `Parabéns! Você atingiu a meta "${goal.titulo}".`,
        type: 'success',
        category: 'financial',
        priority: 'high',
        icon: 'mdi-trophy',
        actions: [
          {
            text: 'Ver Meta',
            action: () => this.$router.push(`/metas/${goal.id}`)
          }
        ]
      })
    },

    notifyBudgetAlert(category, percentage) {
      this.createNotification({
        title: '⚠️ Alerta de Orçamento',
        message: `Você usou ${percentage}% do orçamento de ${category}.`,
        type: 'warning',
        category: 'financial',
        priority: 'high',
        icon: 'mdi-chart-pie',
        actions: [
          {
            text: 'Ver Categorias',
            action: () => this.$router.push('/categorias')
          }
        ]
      })
    },

    notifyLargeTransaction(transaction) {
      this.createNotification({
        title: '💰 Transação Importante',
        message: `${transaction.tipo === 'RECEITA' ? 'Receita' : 'Despesa'} de ${this.formatCurrency(transaction.valor)} registrada.`,
        type: transaction.tipo === 'RECEITA' ? 'success' : 'info',
        category: 'financial',
        priority: 'medium',
        data: { transaction }
      })
    },

    // Management methods
    markAsRead(notificationId) {
      const notification = this.notifications.find(n => n.id === notificationId)
      if (notification) {
        notification.read = true
      }
    },

    markAllAsRead() {
      this.notifications.forEach(n => {
        n.read = true
      })
    },

    dismissNotification(notificationId) {
      const notification = this.notifications.find(n => n.id === notificationId)
      if (notification) {
        notification.dismissed = true
      }
    },

    removeNotification(notificationId) {
      const index = this.notifications.findIndex(n => n.id === notificationId)
      if (index > -1) {
        this.notifications.splice(index, 1)
      }
    },

    removeToast(toastId) {
      const index = this.toasts.findIndex(t => t.id === toastId)
      if (index > -1) {
        this.toasts.splice(index, 1)
      }
    },

    removeSnackbar(snackbarId) {
      const index = this.snackbars.findIndex(s => s.id === snackbarId)
      if (index > -1) {
        this.snackbars.splice(index, 1)
      }
    },

    clearAll() {
      this.notifications = []
      this.toasts = []
      this.snackbars = []
    },

    clearByCategory(category) {
      this.notifications = this.notifications.filter(n => n.category !== category)
    },

    clearExpired() {
      const now = new Date()
      this.notifications = this.notifications.filter(n => {
        return !n.expires_at || new Date(n.expires_at) > now
      })
    },

    // Utility methods
    getDefaultIcon(type) {
      const icons = {
        success: 'mdi-check-circle',
        error: 'mdi-alert-circle',
        warning: 'mdi-alert',
        info: 'mdi-information'
      }
      return icons[type] || 'mdi-bell'
    },

    getTypeColor(type) {
      const colors = {
        success: 'success',
        error: 'error',
        warning: 'warning',
        info: 'info'
      }
      return colors[type] || 'primary'
    },

    formatCurrency(value) {
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      }).format(value || 0)
    },

    playNotificationSound(type) {
      if (!this.preferences.playSound) return
      
      // Simple beep for different types
      const context = new (window.AudioContext || window.webkitAudioContext)()
      const frequencies = {
        success: 800,
        error: 400,
        warning: 600,
        info: 500
      }
      
      const oscillator = context.createOscillator()
      const gainNode = context.createGain()
      
      oscillator.connect(gainNode)
      gainNode.connect(context.destination)
      
      oscillator.frequency.value = frequencies[type] || 500
      oscillator.type = 'sine'
      
      gainNode.gain.setValueAtTime(0.1, context.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, context.currentTime + 0.3)
      
      oscillator.start(context.currentTime)
      oscillator.stop(context.currentTime + 0.3)
    },

    reportError(error, context) {
      // Implement error reporting to backend
      console.error('Error reported:', { error, context })
    },

    // Preferences
    updatePreferences(newPreferences) {
      this.preferences = { ...this.preferences, ...newPreferences }
    },

    // Cleanup old notifications
    cleanup() {
      this.clearExpired()
      
      // Keep only last 100 notifications
      if (this.notifications.length > 100) {
        this.notifications = this.notifications.slice(0, 100)
      }
    }
  }
}) 