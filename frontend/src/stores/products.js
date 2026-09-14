import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

function mapProduct(product) {
  return {
    id: product.id,
    name: product.name,
    category: product.category?.name ?? '',
    // product.image es una ruta relativa (/products/<id>/photo) servida por el
    // backend, no por Vite: hay que anteponer la baseURL de la API o el navegador
    // la busca contra el origen del frontend y nunca carga.
    image: product.image ? `${api.defaults.baseURL}${product.image}` : null,
    price: product.price,
    unitLabel: product.unitLabel,
    badge: product.stock <= 0 ? 'Agotado' : undefined,
  }
}

function buildParams(filters) {
  // URLSearchParams en vez de un objeto plano: axios serializa arrays como
  // species_id[]=1, pero Flask's request.args.getlist() espera la clave
  // repetida sin corchetes (species_id=1&species_id=2).
  const params = new URLSearchParams()

  if (filters.categoryId) {
    params.append('category_id', filters.categoryId)
  } else if (filters.categoryIds?.length) {
    // Sin subcategoria elegida: restringe al scope del tab activo (Mascotas/
    // Ganaderia) mandando todas sus subcategorias - products.category_id
    // siempre guarda la subcategoria (decision 19), nunca el padre.
    filters.categoryIds.forEach((id) => params.append('category_id', id))
  }
  filters.speciesIds.forEach((id) => params.append('species_id', id))
  filters.brands.forEach((brand) => params.append('brand', brand))
  if (filters.minPrice !== null && filters.minPrice !== '')
    params.append('min_price', filters.minPrice)
  if (filters.maxPrice !== null && filters.maxPrice !== '')
    params.append('max_price', filters.maxPrice)
  if (filters.search) params.append('search', filters.search)
  if (filters.sort) params.append('sort', filters.sort)
  params.append('page', filters.page)

  return params
}

export const useProductsStore = defineStore('products', () => {
  const products = ref([])
  const loading = ref(false)
  const error = ref('')

  const facets = ref({ categories: [], species: [], brands: [], price_range: { min: 0, max: 0 } })
  const facetsLoading = ref(false)

  const pagination = ref({ total: 0, page: 1, pages: 1 })

  // Estado aparte para el listado del panel de personal: el publico usa
  // `products`/`mapProduct` (forma reducida para las tarjetas del catalogo),
  // el panel necesita el payload completo (sku, stock, isActive, etc.) y no
  // debe compartir filtros/paginacion con la vista publica de /productos.
  // Top productos mas vendidos (ventas reales, todo el historial) - alimenta
  // tanto el carrusel publico "Productos recomendados" como la seccion
  // "Productos Destacados" del dashboard de personal, mismo endpoint.
  const featuredProducts = ref([])
  const featuredLoading = ref(false)
  const randomProducts = ref([])
  const randomLoading = ref(false)

  const adminProducts = ref([])
  const adminLoading = ref(false)
  const adminError = ref('')
  const adminPagination = ref({ total: 0, page: 1, pages: 1, perPage: 10 })
  const categories = ref([])
  const suppliers = ref([])
  const species = ref([])

  function topCategories() {
    return categories.value.filter((c) => !c.parentId)
  }

  function subcategoriesOf(parentId) {
    if (!parentId) return []
    return categories.value.filter((c) => c.parentId === Number(parentId))
  }

  function topCategoryIdByName(name) {
    const found = categories.value.find((c) => !c.parentId && c.name === name)
    return found ? found.id : null
  }

  function speciesForCategory(categoryId) {
    if (!categoryId) return []
    return species.value.filter((s) => s.categoryId === Number(categoryId))
  }

  const filters = ref({
    categoryId: null,
    categoryIds: [],
    topCategoryId: null,
    speciesIds: [],
    brands: [],
    minPrice: '',
    maxPrice: '',
    search: '',
    sort: '',
    page: 1,
  })

  async function fetchProducts() {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/products', { params: buildParams(filters.value) })
      products.value = data.products.map(mapProduct)
      pagination.value = { total: data.total, page: data.page, pages: data.pages }
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar los productos.'
    } finally {
      loading.value = false
    }
  }

  async function fetchFeaturedProducts(limit = 5) {
    featuredLoading.value = true
    try {
      const { data } = await api.get('/products/featured', { params: { limit } })
      featuredProducts.value = data.products.map((p) => ({ ...mapProduct(p), unitsSold: p.unitsSold }))
    } finally {
      featuredLoading.value = false
    }
  }

  // "Podrían interesarte" (Home público, debajo de Destacados) - excludeIds
  // evita repetir ahi mismo los productos que ya salieron en Destacados.
  async function fetchRandomProducts(limit = 8, excludeIds = []) {
    randomLoading.value = true
    try {
      const params = { limit }
      if (excludeIds.length) params.exclude = excludeIds.join(',')
      const { data } = await api.get('/products/random', { params })
      randomProducts.value = data.products.map(mapProduct)
    } finally {
      randomLoading.value = false
    }
  }

  async function fetchFacets() {
    facetsLoading.value = true
    try {
      const { data } = await api.get('/products/filters')
      facets.value = data
    } finally {
      facetsLoading.value = false
    }
  }

  function setPage(page) {
    filters.value.page = page
    fetchProducts()
  }

  function applyFilters() {
    filters.value.page = 1
    fetchProducts()
  }

  // Sin topCategoryId explicito, conserva el tab (Mascotas/Ganaderia) activo -
  // "Limpiar filtros" no debe sacar al usuario del scope en el que esta.
  function resetFilters(topCategoryId = filters.value.topCategoryId) {
    // Incluye siempre el propio topCategoryId, no solo sus subcategorias:
    // Ganaderia todavia no tiene ninguna subcategoria creada, y un scope sin
    // ids no filtra nada (mostraria productos de Mascotas). Un producto real
    // nunca tiene category_id = id de un nivel 1 (decision 19), asi que este
    // id de mas no cambia el resultado cuando si hay subcategorias.
    const categoryIds = topCategoryId
      ? [topCategoryId, ...subcategoriesOf(topCategoryId).map((c) => c.id)]
      : []
    filters.value = {
      categoryId: null,
      categoryIds,
      topCategoryId,
      speciesIds: [],
      brands: [],
      minPrice: '',
      maxPrice: '',
      search: '',
      sort: '',
      page: 1,
    }
    fetchProducts()
  }

  async function fetchAdminProducts({ search, categoryId, speciesId, status, page = 1, perPage = 10 } = {}) {
    adminLoading.value = true
    adminError.value = ''
    try {
      const params = new URLSearchParams()
      params.append('per_page', perPage)
      params.append('page', page)
      if (search) params.append('search', search)
      if (categoryId) params.append('category_id', categoryId)
      if (speciesId) params.append('species_id', speciesId)
      params.append('status', status || 'active')
      const { data } = await api.get('/products', { params })
      adminProducts.value = data.products
      adminPagination.value = { total: data.total, page: data.page, pages: data.pages, perPage: data.per_page }
    } catch (err) {
      adminError.value = err.response?.data?.message || 'No se pudieron cargar los productos.'
    } finally {
      adminLoading.value = false
    }
  }

  async function fetchCategories() {
    const { data } = await api.get('/catalog/categories')
    categories.value = data
  }

  async function fetchSuppliers() {
    const { data } = await api.get('/catalog/suppliers')
    suppliers.value = data
  }

  async function fetchSpecies() {
    const { data } = await api.get('/catalog/species')
    species.value = data
  }

  async function fetchProduct(id) {
    const { data } = await api.get(`/products/${id}`)
    return data
  }

  async function suggestSku(categoryId) {
    const { data } = await api.get('/products/suggest-sku', { params: { category_id: categoryId } })
    return data.sku
  }

  async function createProduct(formData) {
    const { data } = await api.post('/products', formData)
    return data
  }

  async function updateProduct(id, formData) {
    const { data } = await api.put(`/products/${id}`, formData)
    return data
  }

  async function deleteProduct(id) {
    await api.delete(`/products/${id}`)
  }

  async function deactivateProduct(id) {
    const { data } = await api.put(`/products/${id}`, { isActive: false })
    return data
  }

  async function reactivateProduct(id) {
    const { data } = await api.put(`/products/${id}`, { isActive: true })
    return data
  }

  return {
    products,
    loading,
    error,
    facets,
    facetsLoading,
    pagination,
    filters,
    featuredProducts,
    featuredLoading,
    fetchFeaturedProducts,
    randomProducts,
    randomLoading,
    fetchRandomProducts,
    fetchProducts,
    fetchFacets,
    setPage,
    applyFilters,
    resetFilters,
    fetchProduct,
    suggestSku,
    createProduct,
    updateProduct,
    deleteProduct,
    adminProducts,
    adminLoading,
    adminError,
    adminPagination,
    fetchAdminProducts,
    categories,
    fetchCategories,
    topCategories,
    subcategoriesOf,
    topCategoryIdByName,
    suppliers,
    fetchSuppliers,
    species,
    fetchSpecies,
    speciesForCategory,
    deactivateProduct,
    reactivateProduct,
  }
})
