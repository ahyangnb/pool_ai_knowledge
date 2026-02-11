import axios from 'axios'

const request = axios.create({
  baseURL: '',
  timeout: 30000,
})

request.interceptors.request.use((config) => {
  const language = localStorage.getItem('language') || 'zh-CN'
  if (config.method === 'get') {
    config.params = { ...config.params, language }
  } else if (config.data && typeof config.data === 'object') {
    if (!config.data.language) {
      config.data = { ...config.data, language }
    }
  } else if (!config.data) {
    config.data = { language }
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code !== 0) {
      return Promise.reject(new Error(res.message || 'Request failed'))
    }
    return res.data
  },
  (error) => {
    return Promise.reject(error)
  }
)

export default request
