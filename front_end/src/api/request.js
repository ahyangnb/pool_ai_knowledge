import axios from 'axios'

const request = axios.create({
  baseURL: '',
  timeout: 30000,
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
