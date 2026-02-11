import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/api/admin/login',
    method: 'post',
    baseURL: '',
    data
  })
}

export function getInfo() {
  return request({
    url: '/api/admin/me',
    method: 'get',
    baseURL: ''
  })
}

export function logout() {
  return request({
    url: '/api/admin/logout',
    method: 'post',
    baseURL: ''
  })
}
