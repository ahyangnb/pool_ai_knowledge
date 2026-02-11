import request from '@/utils/request'

export function fetchEffectiveKeys() {
  return request({
    url: '/api/admin/api-keys/effective',
    method: 'get',
    baseURL: ''
  })
}

export function saveApiKey(data) {
  return request({
    url: '/api/admin/api-keys',
    method: 'post',
    baseURL: '',
    data
  })
}
