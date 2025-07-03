<template>
  <v-card
    :class="cardClasses"
    :elevation="elevation"
    :hover="hover"
    :loading="loading"
  >
    <!-- Header -->
    <v-card-title v-if="title || $slots.title" :class="titleClasses">
      <slot name="title">
        <div class="d-flex align-center">
          <v-icon v-if="icon" :icon="icon" class="mr-3" />
          <span>{{ title }}</span>
        </div>
      </slot>
    </v-card-title>

    <!-- Subtitle -->
    <v-card-subtitle v-if="subtitle || $slots.subtitle">
      <slot name="subtitle">
        {{ subtitle }}
      </slot>
    </v-card-subtitle>

    <!-- Content -->
    <v-card-text v-if="$slots.default" :class="contentClasses">
      <slot />
    </v-card-text>

    <!-- Actions -->
    <v-card-actions v-if="$slots.actions" class="pa-4">
      <slot name="actions" />
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  elevation: {
    type: [String, Number],
    default: 2
  },
  hover: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  color: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'elevated'
  },
  rounded: {
    type: [String, Boolean],
    default: 'lg'
  },
  border: {
    type: Boolean,
    default: false
  },
  density: {
    type: String,
    default: 'default'
  }
})

// Computed
const cardClasses = computed(() => [
  'base-card',
  {
    [`base-card--${props.color}`]: props.color,
    'base-card--border': props.border
  }
])

const titleClasses = computed(() => [
  'base-card__title',
  {
    'pa-4 pb-2': props.density === 'default',
    'pa-3 pb-1': props.density === 'compact',
    'pa-2 pb-1': props.density === 'comfortable'
  }
])

const contentClasses = computed(() => [
  'base-card__content',
  {
    'pa-4': props.density === 'default',
    'pa-3': props.density === 'compact',
    'pa-2': props.density === 'comfortable'
  }
])
</script>

<style scoped>
.base-card {
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.base-card--border {
  border: 1px solid rgba(var(--v-theme-surface), 0.12);
}

.base-card__title {
  font-weight: 600;
  color: rgb(var(--v-theme-on-surface));
}

.base-card__content {
  color: rgba(var(--v-theme-on-surface), 0.87);
}

/* Color variants */
.base-card--primary {
  background: rgba(var(--v-theme-primary), 0.05);
  border-left: 4px solid rgb(var(--v-theme-primary));
}

.base-card--success {
  background: rgba(var(--v-theme-success), 0.05);
  border-left: 4px solid rgb(var(--v-theme-success));
}

.base-card--error {
  background: rgba(var(--v-theme-error), 0.05);
  border-left: 4px solid rgb(var(--v-theme-error));
}

.base-card--warning {
  background: rgba(var(--v-theme-warning), 0.05);
  border-left: 4px solid rgb(var(--v-theme-warning));
}

.base-card--info {
  background: rgba(var(--v-theme-info), 0.05);
  border-left: 4px solid rgb(var(--v-theme-info));
}

/* Hover effect */
.base-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

/* Loading state */
.base-card--loading {
  opacity: 0.7;
  pointer-events: none;
}
</style> 