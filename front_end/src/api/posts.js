import request from './request'

export function getPosts(params) {
  return request.get('/api/web/posts', { params })
}

export function getPost(id) {
  return request.get(`/api/web/posts/${id}`)
}

export function searchPosts(query, topK = 3) {
  return request.post('/api/web/search', { query, top_k: topK })
}
