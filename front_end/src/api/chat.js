import request from './request'

export function chatWithAgent(message, agentName = 'knowledge') {
  return request.post('/api/chat', {
    agent_name: agentName,
    message,
  })
}
