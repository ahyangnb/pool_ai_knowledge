import request from '@/utils/request'

export function fetchPostList(query) {
  return request({
    url: '/api/admin/posts',
    method: 'get',
    baseURL: '',
    params: query
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
