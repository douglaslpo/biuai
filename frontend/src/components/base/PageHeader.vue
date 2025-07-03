<template>
  <div class="page-header">
    <div class="header-content">
      <div class="header-info">
        <h1 class="page-title">
          <v-icon 
            v-if="icon" 
            :icon="icon" 
            size="large" 
            class="mr-3"
            :color="iconColor"
          />
          {{ title }}
        </h1>
        <p v-if="subtitle" class="page-subtitle">
          {{ subtitle }}
        </p>
        <div v-if="breadcrumbs && breadcrumbs.length" class="breadcrumbs mt-2">
          <v-breadcrumbs :items="breadcrumbs" density="compact">
            <template v-slot:divider>
              <v-icon size="16">mdi-chevron-right</v-icon>
            </template>
          </v-breadcrumbs>
        </div>
      </div>
      
      <div v-if="$slots.actions" class="header-actions">
        <slot name="actions" />
      </div>
    </div>
    
    <!-- Metrics Row -->
    <div v-if="$slots.metrics" class="header-metrics mt-6">
      <slot name="metrics" />
    </div>
  </div>
</template>

<script setup>
// Props
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  iconColor: {
    type: String,
    default: 'primary'
  },
  breadcrumbs: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.header-info {
  flex: 1;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: rgb(var(--v-theme-primary));
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
}

.page-subtitle {
  font-size: 1.1rem;
  color: rgba(var(--v-theme-on-surface), 0.7);
  margin: 0;
  line-height: 1.5;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  flex-shrink: 0;
}

.breadcrumbs {
  opacity: 0.8;
}

/* Responsividade */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .page-title {
    font-size: 1.75rem;
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
  
  .header-actions {
    justify-content: stretch;
  }
  
  .header-actions :deep(.v-btn) {
    flex: 1;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.5rem;
  }
  
  .header-actions {
    flex-direction: column;
  }
}
</style> 