import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'

export function usePerformanceOptimization() {
  // States
  const initialLoading = ref(true)
  const loadingComponents = ref(new Set())
  const performanceMetrics = ref({
    componentLoadTime: 0,
    dataLoadTime: 0,
    renderTime: 0,
    memoryUsage: 0,
    lastUpdate: null
  })

  // Performance tracking
  const startTime = ref(null)
  const componentStartTimes = ref(new Map())

  // Computed
  const isLoading = computed(() => {
    return initialLoading.value || loadingComponents.value.size > 0
  })

  const loadingProgress = computed(() => {
    if (initialLoading.value) return 0
    const total = 10 // Total expected components/operations
    const loaded = total - loadingComponents.value.size
    return Math.min(100, (loaded / total) * 100)
  })

  // Methods
  const startInitialLoading = () => {
    initialLoading.value = true
    startTime.value = performance.now()
  }

  const finishInitialLoading = async () => {
    await nextTick()
    
    if (startTime.value) {
      performanceMetrics.value.componentLoadTime = performance.now() - startTime.value
    }
    
    // Simular delay mínimo para UX suave
    const minLoadTime = 1000
    const elapsed = performance.now() - (startTime.value || 0)
    
    if (elapsed < minLoadTime) {
      await new Promise(resolve => setTimeout(resolve, minLoadTime - elapsed))
    }
    
    initialLoading.value = false
    measureMemoryUsage()
    performanceMetrics.value.lastUpdate = new Date()
  }

  const addLoadingComponent = (componentName) => {
    loadingComponents.value.add(componentName)
    componentStartTimes.value.set(componentName, performance.now())
  }

  const removeLoadingComponent = (componentName) => {
    loadingComponents.value.delete(componentName)
    
    if (componentStartTimes.value.has(componentName)) {
      const loadTime = performance.now() - componentStartTimes.value.get(componentName)
      componentStartTimes.value.delete(componentName)
      
      // Log component load time for monitoring
      console.debug(`Component ${componentName} loaded in ${loadTime.toFixed(2)}ms`)
    }
  }

  const trackDataLoading = async (operation, operationFn) => {
    const startTime = performance.now()
    addLoadingComponent(`data-${operation}`)
    
    try {
      const result = await operationFn()
      return result
    } finally {
      const loadTime = performance.now() - startTime
      performanceMetrics.value.dataLoadTime += loadTime
      removeLoadingComponent(`data-${operation}`)
    }
  }

  const trackRenderTime = (componentName, renderFn) => {
    const startTime = performance.now()
    
    const result = renderFn()
    
    nextTick(() => {
      const renderTime = performance.now() - startTime
      performanceMetrics.value.renderTime += renderTime
      console.debug(`Component ${componentName} rendered in ${renderTime.toFixed(2)}ms`)
    })
    
    return result
  }

  const measureMemoryUsage = () => {
    if ('memory' in performance) {
      performanceMetrics.value.memoryUsage = performance.memory.usedJSHeapSize / (1024 * 1024) // MB
    }
  }

  // Cache management
  const cache = ref(new Map())
  const cacheExpiry = ref(new Map())
  const defaultCacheDuration = 5 * 60 * 1000 // 5 minutes

  const getCachedData = (key) => {
    if (!cache.value.has(key)) return null
    
    const expiry = cacheExpiry.value.get(key)
    if (expiry && Date.now() > expiry) {
      cache.value.delete(key)
      cacheExpiry.value.delete(key)
      return null
    }
    
    return cache.value.get(key)
  }

  const setCachedData = (key, data, duration = defaultCacheDuration) => {
    cache.value.set(key, data)
    cacheExpiry.value.set(key, Date.now() + duration)
  }

  const clearCache = () => {
    cache.value.clear()
    cacheExpiry.value.clear()
  }

  // Debouncing utility
  const debounceTimers = ref(new Map())

  const debounce = (key, fn, delay = 300) => {
    if (debounceTimers.value.has(key)) {
      clearTimeout(debounceTimers.value.get(key))
    }
    
    const timer = setTimeout(() => {
      fn()
      debounceTimers.value.delete(key)
    }, delay)
    
    debounceTimers.value.set(key, timer)
  }

  // Resource preloading
  const preloadedResources = ref(new Set())

  const preloadImage = (src) => {
    if (preloadedResources.value.has(src)) return Promise.resolve()
    
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => {
        preloadedResources.value.add(src)
        resolve()
      }
      img.onerror = reject
      img.src = src
    })
  }

  const preloadComponent = async (componentLoader) => {
    try {
      const component = await componentLoader()
      return component
    } catch (error) {
      console.error('Error preloading component:', error)
      return null
    }
  }

  // Virtual scrolling utilities
  const createVirtualList = (items, itemHeight = 50, containerHeight = 400) => {
    const visibleStart = ref(0)
    const visibleEnd = ref(Math.ceil(containerHeight / itemHeight))
    
    const updateVisibleRange = (scrollTop) => {
      const start = Math.floor(scrollTop / itemHeight)
      const end = start + Math.ceil(containerHeight / itemHeight) + 1
      
      visibleStart.value = Math.max(0, start)
      visibleEnd.value = Math.min(items.length, end)
    }
    
    const visibleItems = computed(() => {
      return items.slice(visibleStart.value, visibleEnd.value).map((item, index) => ({
        ...item,
        index: visibleStart.value + index,
        top: (visibleStart.value + index) * itemHeight
      }))
    })
    
    const totalHeight = computed(() => items.length * itemHeight)
    
    return {
      visibleItems,
      totalHeight,
      updateVisibleRange,
      visibleStart,
      visibleEnd
    }
  }

  // Intersection Observer for lazy loading
  const intersectionObserver = ref(null)
  const observedElements = ref(new Map())

  const observeElement = (element, callback, options = {}) => {
    if (!intersectionObserver.value) {
      intersectionObserver.value = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          const callback = observedElements.value.get(entry.target)
          if (callback) {
            callback(entry)
          }
        })
      }, {
        rootMargin: '50px',
        threshold: 0.1,
        ...options
      })
    }
    
    observedElements.value.set(element, callback)
    intersectionObserver.value.observe(element)
  }

  const unobserveElement = (element) => {
    if (intersectionObserver.value) {
      intersectionObserver.value.unobserve(element)
      observedElements.value.delete(element)
    }
  }

  // Performance monitoring
  const performanceObserver = ref(null)

  const startPerformanceMonitoring = () => {
    if ('PerformanceObserver' in window) {
      performanceObserver.value = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach(entry => {
          if (entry.entryType === 'measure') {
            console.debug(`Performance measure: ${entry.name} - ${entry.duration.toFixed(2)}ms`)
          }
        })
      })
      
      performanceObserver.value.observe({ entryTypes: ['measure', 'navigation'] })
    }
  }

  const stopPerformanceMonitoring = () => {
    if (performanceObserver.value) {
      performanceObserver.value.disconnect()
      performanceObserver.value = null
    }
  }

  // Memory leak prevention
  const eventListeners = ref([])

  const addEventListenerSafe = (element, event, handler, options) => {
    element.addEventListener(event, handler, options)
    eventListeners.value.push({ element, event, handler, options })
  }

  const removeAllEventListeners = () => {
    eventListeners.value.forEach(({ element, event, handler, options }) => {
      element.removeEventListener(event, handler, options)
    })
    eventListeners.value = []
  }

  // Cleanup utility
  const cleanup = () => {
    // Clear timers
    debounceTimers.value.forEach(timer => clearTimeout(timer))
    debounceTimers.value.clear()
    
    // Clear cache
    clearCache()
    
    // Stop observers
    if (intersectionObserver.value) {
      intersectionObserver.value.disconnect()
    }
    
    stopPerformanceMonitoring()
    
    // Remove event listeners
    removeAllEventListeners()
    
    // Clear component tracking
    loadingComponents.value.clear()
    componentStartTimes.value.clear()
  }

  // Auto cleanup
  onMounted(() => {
    startPerformanceMonitoring()
    measureMemoryUsage()
    
    // Measure memory usage periodically
    const memoryInterval = setInterval(measureMemoryUsage, 30000) // Every 30 seconds
    
    onUnmounted(() => {
      clearInterval(memoryInterval)
      cleanup()
    })
  })

  onUnmounted(() => {
    cleanup()
  })

  return {
    // States
    initialLoading,
    isLoading,
    loadingProgress,
    performanceMetrics,

    // Loading management
    startInitialLoading,
    finishInitialLoading,
    addLoadingComponent,
    removeLoadingComponent,
    trackDataLoading,
    trackRenderTime,

    // Cache management
    getCachedData,
    setCachedData,
    clearCache,

    // Utilities
    debounce,
    preloadImage,
    preloadComponent,
    createVirtualList,
    observeElement,
    unobserveElement,
    addEventListenerSafe,

    // Performance
    measureMemoryUsage,
    startPerformanceMonitoring,
    stopPerformanceMonitoring,

    // Cleanup
    cleanup
  }
} 