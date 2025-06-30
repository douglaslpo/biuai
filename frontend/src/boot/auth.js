import { api } from './axios'

const auth = {
  // Verifica se o usuário está autenticado
  isAuthenticated () {
    return !!localStorage.getItem('token')
  },

  // Faz login
  async login (email, senha) {
    const response = await api.post('/auth/token', {
      username: email,
      password: senha
    })
    const { access_token } = response.data
    localStorage.setItem('token', access_token)
    return response.data
  },

  // Faz logout
  logout () {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },

  // Registra um novo usuário
  async register (userData) {
    const response = await api.post('/auth/registro', userData)
    return response.data
  },

  // Obtém o token atual
  getToken () {
    return localStorage.getItem('token')
  },

  // Obtém os dados do usuário atual
  async getCurrentUser () {
    const response = await api.get('/auth/me')
    return response.data
  }
}

export default auth 