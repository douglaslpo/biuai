import { ref, computed } from 'vue'
import { useLoading } from './useLoading'

export function usePageData(config = {}) {
  const {
    initialData = [],
    fetchFn = null,
    autoFetch = true,
    pageSize = 20
  } = config

  // States
  const data = ref(initialData)
  const error = ref(null)
  const { loading, setLoading } = useLoading()
  
  // Pagination
  const currentPage = ref(1)
  const totalItems = ref(0)
  const itemsPerPage = ref(pageSize)
  
  // Search and Filters
  const searchQuery = ref('')
  const filters = ref({})
  const sortBy = ref('')
  const sortOrder = ref('asc')

  // Computed
  const hasData = computed(() => data.value && data.value.length > 0)
  const isEmpty = computed(() => !loading.value && !hasData.value)
  const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value))
  
  const filteredData = computed(() => {
    let result = [...data.value]
    
    // Apply search
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      result = result.filter(item => 
        Object.values(item).some(value => 
          String(value).toLowerCase().includes(query)
        )
      )
    }
    
    // Apply filters
    Object.entries(filters.value).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        result = result.filter(item => {
          if (Array.isArray(value)) {
            return value.includes(item[key])
          }
          return item[key] === value
        })
      }
    })
    
    // Apply sorting
    if (sortBy.value) {
      result.sort((a, b) => {
        const aVal = a[sortBy.value]
        const bVal = b[sortBy.value]
        
        if (sortOrder.value === 'desc') {
          return bVal > aVal ? 1 : -1
        }
        return aVal > bVal ? 1 : -1
      })
    }
    
    return result
  })

  const paginatedData = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return filteredData.value.slice(start, end)
  })

  // Methods
  const fetchData = async (params = {}) => {
    if (!fetchFn) {
      console.warn('usePageData: fetchFn not provided')
      return
    }

    try {
      setLoading(true)
      error.value = null
      
      const response = await fetchFn({
        page: currentPage.value,
        pageSize: itemsPerPage.value,
        search: searchQuery.value,
        filters: filters.value,
        sortBy: sortBy.value,
        sortOrder: sortOrder.value,
        ...params
      })
      
      if (response.data) {
        data.value = response.data
        totalItems.value = response.total || response.data.length
      } else {
        data.value = response
        totalItems.value = response.length
      }
      
    } catch (err) {
      console.error('Error fetching data:', err)
      error.value = err.message || 'Erro ao carregar dados'
    } finally {
      setLoading(false)
    }
  }

  const refresh = () => {
    return fetchData()
  }

  const setFilter = (key, value) => {
    filters.value[key] = value
    currentPage.value = 1 // Reset to first page
    
    if (autoFetch && fetchFn) {
      fetchData()
    }
  }

  const clearFilters = () => {
    filters.value = {}
    searchQuery.value = ''
    currentPage.value = 1
    
    if (autoFetch && fetchFn) {
      fetchData()
    }
  }

  const setSearch = (query) => {
    searchQuery.value = query
    currentPage.value = 1
    
    if (autoFetch && fetchFn) {
      fetchData()
    }
  }

  const setSorting = (field, order = 'asc') => {
    sortBy.value = field
    sortOrder.value = order
    
    if (autoFetch && fetchFn) {
      fetchData()
    }
  }

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
      
      if (autoFetch && fetchFn) {
        fetchData()
      }
    }
  }

  const addItem = (item) => {
    data.value.unshift(item)
    totalItems.value += 1
  }

  const updateItem = (id, updatedItem) => {
    const index = data.value.findIndex(item => item.id === id)
    if (index !== -1) {
      data.value[index] = { ...data.value[index], ...updatedItem }
    }
  }

  const removeItem = (id) => {
    const index = data.value.findIndex(item => item.id === id)
    if (index !== -1) {
      data.value.splice(index, 1)
      totalItems.value -= 1
    }
  }

  // Auto fetch on mount
  if (autoFetch && fetchFn) {
    fetchData()
  }

  return {
    // State
    data,
    filteredData,
    paginatedData,
    loading,
    error,
    
    // Pagination
    currentPage,
    totalItems,
    totalPages,
    itemsPerPage,
    
    // Search & Filters
    searchQuery,
    filters,
    sortBy,
    sortOrder,
    
    // Computed
    hasData,
    isEmpty,
    
    // Methods
    fetchData,
    refresh,
    setFilter,
    clearFilters,
    setSearch,
    setSorting,
    goToPage,
    addItem,
    updateItem,
    removeItem
  }
} 