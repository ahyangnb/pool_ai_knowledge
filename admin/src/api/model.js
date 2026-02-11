import request from '@/utils/request'

export function fetchModels() {
  return request({
    url: '/api/admin/models',
    method: 'get',
    baseURL: ''
  })
}

export function switchModel(model) {
  return request({
    url: '/api/admin/models/current',
    method: 'put',
    baseURL: '',
    data: { model }
  })
}
