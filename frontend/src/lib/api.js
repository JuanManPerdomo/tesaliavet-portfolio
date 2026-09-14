import axios from 'axios'

const TOKEN_KEY = 'tesaliavet_token'
const REFRESH_TOKEN_KEY = 'tesaliavet_refresh_token'
const USER_KEY = 'tesaliavet_user'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

// El access token dura 1h, no 7 dias fijos como antes (decision 8/Next Steps
// #3 en CLAUDE.md) - cuando una request cae en 401 por token vencido, se pide
// uno nuevo con el refresh token (30 dias) y se reintenta una sola vez. Usa
// axios "pelado" (no la instancia `api`) para esa llamada: si pasara por el
// interceptor de arriba mandaria el access token vencido en vez del refresh
// token. refreshPromise compartida evita disparar varios refresh a la vez
// cuando varias requests caen en 401 al mismo tiempo.
let refreshPromise = null

function requestNewAccessToken() {
  if (!refreshPromise) {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
    if (!refreshToken) {
      refreshPromise = Promise.reject(new Error('No hay sesión para renovar'))
    } else {
      refreshPromise = axios
        .post(`${api.defaults.baseURL}/auth/refresh`, null, {
          headers: { Authorization: `Bearer ${refreshToken}` },
        })
        .then(({ data }) => {
          localStorage.setItem(TOKEN_KEY, data.token)
          return data.token
        })
        .finally(() => {
          refreshPromise = null
        })
    }
  }
  return refreshPromise
}

const AUTH_ENDPOINTS_WITHOUT_RETRY = ['/auth/login', '/auth/register', '/auth/refresh']

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error
    const isAuthEndpoint = AUTH_ENDPOINTS_WITHOUT_RETRY.some((path) => config?.url?.startsWith(path))

    if (response?.status === 401 && !isAuthEndpoint && !config._retriedAfterRefresh) {
      config._retriedAfterRefresh = true
      try {
        const newToken = await requestNewAccessToken()
        config.headers.Authorization = `Bearer ${newToken}`
        return api(config)
      } catch {
        clearSession()
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
