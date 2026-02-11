import request from '@/utils/request'

export function fetchPostList(query) {
  const params = {
    skip: ((query.page || 1) - 1) * (query.limit || 20),
    limit: query.limit || 20,
    ...(query.language ? { language: query.language } : {})
  }
  return request({
    url: '/api/admin/posts',
    method: 'get',
    baseURL: '',
    params
  })
}

export function fetchPost(id) {
  return request({
    url: `/api/admin/posts/${id}`,
    method: 'get',
    baseURL: ''
  })
}

export function createPost(data) {
  return request({
    url: '/api/admin/posts',
    method: 'post',
    baseURL: '',
    data
  })
}

export function updatePost(id, data) {
  return request({
    url: `/api/admin/posts/${id}`,
    method: 'put',
    baseURL: '',
    data
  })
}

export function deletePost(id) {
  return request({
    url: `/api/admin/posts/${id}`,
    method: 'delete',
    baseURL: ''
  })
}
