import { ref } from "vue"
import axios from "axios"


const token = ref(null)
const api = axios.create({
  baseURL: '/api'
})

api.interceptors.request.use(async (config) => {
  if (token.value) {
    config.headers.Authorization = `Bearer ${token.value}`
  }
  return config
})

function init(pToken) {
  token.value = pToken
}

async function fetchMeta() {
  const response = await api.get('/meta')
  return response.data
}

// Fetch the layers for date
async function fetchLayers(date) {
  const response = await api.get(`/layers?date=${date}`)
  return response.data.sort((a, b) => a.zlevel - b.zlevel)
}

export {
  init, fetchMeta, fetchLayers
}