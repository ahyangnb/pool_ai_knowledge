import request from './request'

export function chatWithAgent(message, { agentName = 'knowledge', postId, language } = {}) {
  const data = { agent_name: agentName, message }
  if (postId) data.post_id = postId
  if (language) data.language = language
  return request.post('/api/chat', data)
}
